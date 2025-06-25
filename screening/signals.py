from hashlib import md5
from collections import defaultdict
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.core.cache import cache
from screening.models import QuestionaryResponse
from rozumity.utils import rel


@receiver(post_save, sender=QuestionaryResponse, dispatch_uid='response.changed')
async def handle_response_answers_change(sender, instance, created, **kwargs):
    answers = getattr(instance, '_answers_from_request', [])
    scores_map = getattr(instance, '_scores_map', [])
    #await cache.adelete(
    #    f"{md5(instance.__class__.__name__.lower().encode()).hexdigest()}:{instance.pk}"
    #)
    if isinstance(answers, list) and len(answers):
        through = QuestionaryResponse.answers.through
        await through.objects.abulk_create([
            through(response=instance, answer=answer) for answer in answers
        ], ignore_conflicts=True)
        await m2m_changed.asend_robust(
            sender=through, instance=instance, action='post_add', reverse=False, 
            model=through, using='default', pk_set={answer.pk for answer in answers}
        )
    elif isinstance(scores_map, dict) and len(scores_map.keys()):
        scores_map = instance.scores_map or {}
        all_scores = [s async for s in instance.questionary.scores.all()]
        scores_by_dim = defaultdict(list)
        for score in all_scores:
            scores_by_dim[str(score.dimension_id)].append(score)
        found_scores = [min([
            s for s in scores_by_dim.get(str(dim_id), [])
            if s.min_score < value <= s.max_score
        ], key=lambda s: (
            s.max_score - s.min_score,
            abs((s.max_score + s.min_score) / 2 - value)
        )) for dim_id, value in scores_map.items()]
        if found_scores:
            await instance.scores.aadd(found_scores[0].pk)
    else:
        await cache.adelete(
            f"{md5(instance.__class__.__name__.lower().encode()).hexdigest()}:{instance.pk}"
        )


@receiver(m2m_changed, sender=QuestionaryResponse.answers.through, dispatch_uid='response.changed_answers')
async def calc_response_scores_map(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action != 'post_add':
        return
    try:
        del instance._answers_from_request
    except AttributeError:
        pass
    if instance.is_filled:
        instance.is_filled, instance.is_checked = False, False
        await instance.asave()
        await instance.scores.aclear()
        await instance.scores_extra.aclear()
    questionary = await rel(instance, 'questionary')
    questions_q = questionary.questions.all()
    answers_q = instance.answers.all()
    if await answers_q.acount() >= await questions_q.acount():
        question_ids = [q async for q in questions_q.values_list("id", flat=True)]
        answer_question_ids = [a async for a in answers_q.values_list("question_id", flat=True)]
        is_filled = set(question_ids).issubset(set(answer_question_ids))
        if is_filled:
            instance.is_filled = is_filled
            await instance.asave()
    if not instance.is_filled:
        return
    answer_ids = [id async for id in instance.answers.values_list('id', flat=True)]
    dimvals_model = instance._meta.get_field('answers').remote_field.model._meta.get_field('dimensions').remote_field.through
    dimvals = [
        d async for d in dimvals_model.objects.filter(answer_id__in=answer_ids)
        .values('dimension_id', 'value')
    ]
    scores_map = defaultdict(float)
    for d in dimvals:
        scores_map[d['dimension_id']] += d['value']
    instance._scores_map = {dim_id: value for dim_id, value in scores_map.items()}
    instance.scores_map = instance._scores_map
    await cache.adelete(
        f"{md5(instance.__class__.__name__.lower().encode()).hexdigest()}:{instance.pk}"
    )
    await instance.answers.aclear()
    await instance.asave()


@receiver(m2m_changed, sender=QuestionaryResponse.scores.through, dispatch_uid='response.changed_scores')
async def handle_response_scores_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action != 'post_add':
        return
    try:
        del instance._scores_map
    except AttributeError:
        pass
    score_ids = set([s.id async for s in instance.scores.all()])
    extra_scores_model = instance._meta.get_field('scores_extra').remote_field.model
    extras = [e async for e in extra_scores_model.objects.filter(
        questionary=instance.questionary
    ).prefetch_related('scores')]
    for extra in extras:
        extra_score_ids = set([s.id for s in extra.scores.all()])
        if extra_score_ids and extra_score_ids.issubset(score_ids):
            await instance.scores_extra.aset([extra])
    instance.is_checked = True
    await instance.asave()
