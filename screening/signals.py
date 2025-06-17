from collections import defaultdict
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from asgiref.sync import sync_to_async

from rozumity.utils import rel

from .models import QuestionaryResponse, QuestionaryScore, QuestionaryScoreExtra


@receiver(m2m_changed, sender=QuestionaryResponse.answers.through, dispatch_uid='response.answer_changed')
async def response_answer_changed(sender, instance, action, **kwargs):
    # Check that all answers are provided (is_filled)
    if not await instance.is_filled:
        return

    # 1. Collect dimension values from the user's answers
    dimension_values = {dim_id: value for dim_id, value in await sync_to_async(list)(
        instance.answers.through.objects.filter(
            answer_id__in=await sync_to_async(list)(
                instance.answers.values_list('id', flat=True)
            )
        ).values_list(
            'questionarydimensionvalue__dimension_id', 
            'questionarydimensionvalue__value'
        )
    )}

    # 2. Fetch all matching scores in a single query
    all_scores = await sync_to_async(list)(
        QuestionaryScore.objects.filter(
            questionary=instance.questionary,
            dimension_id__in=dimension_values.keys()
        )
    )

    # 2.1. Group scores by dimension_id
    scores_by_dim = defaultdict(list)
    for score in all_scores:
        scores_by_dim[score.dimension_id].append(score)

    # 2.2. For each dimension, select the best score (narrowest range, closest to the value)
    found_scores = []
    for dim_id, value in dimension_values.items():
        candidates = [
            s for s in scores_by_dim.get(dim_id, [])
            if s.min_score <= value <= s.max_score
        ]
        if candidates:
            found_scores.append(min(
                candidates,
                key=lambda s: (
                    s.max_score - s.min_score,
                    abs((s.max_score + s.min_score) / 2 - value)
                )
            ))
    await instance.scores.aset(found_scores)

    # 3. Check extra results (whether all dimensions match)
    async for extra in QuestionaryScoreExtra.objects.filter(questionary=instance.questionary).prefetch_related('scores').all():
        extra_dim_ids = set(es.dimension_id for es in list(extra.scores.all()))
        if extra_dim_ids and extra_dim_ids.issubset(set(s.dimension_id for s in found_scores)):
            await instance.scores_extra.aset([extra])
            break  # Only the first matching one
    

@receiver(m2m_changed, sender=QuestionaryResponse.scores.through, dispatch_uid='response.scores_changed')
async def scores_changed(sender, instance, action, **kwargs):
    if action not in ['post_add', 'post_remove', 'post_clear']:
        return

    # 1. Get all dimension IDs that already have a score
    scored_dim_ids = set(await sync_to_async(list)(
        instance.scores.all().values_list('dimension_id', flat=True)
    ))

    # 2. Assign first matching scores_extra (if its required dimensions are all scored)
    async for extra in QuestionaryScoreExtra.objects.filter(
        questionary=instance.questionary
    ).prefetch_related('scores'):
        extra_dim_ids = {
            s.dimension_id for s 
            in await sync_to_async(list)(extra.scores.all())
        }
        if extra_dim_ids and extra_dim_ids.issubset(scored_dim_ids):
            await instance.scores_extra.aset([extra])
            break

    # 3. Check completeness: all dimensions from answers must be scored
    if set(await sync_to_async(list)(instance.answers.through.objects.filter(
        questionaryresponse_id=instance.pk
    ).values_list(
        'questionarydimensionvalue__dimension_id', flat=True
    ).distinct())).issubset(scored_dim_ids):
        instance.is_checked = True
        await instance.asave(update_fields=["is_checked"])
