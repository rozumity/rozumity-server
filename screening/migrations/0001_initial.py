# Generated by Django 5.2.1 on 2025-06-14 14:10

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionaryCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255, unique=True)),
                ('description', models.TextField(default='')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Category Questionary',
                'verbose_name_plural': 'Q - Categories',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='QuestionaryDimension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255, unique=True)),
                ('description', models.TextField(default='')),
            ],
            options={
                'verbose_name': 'Dimension',
                'verbose_name_plural': 'Q - Dimensions',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='SurveyCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255, unique=True)),
                ('description', models.TextField(default='')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Category Survey',
                'verbose_name_plural': 'S - Categories',
            },
        ),
        migrations.CreateModel(
            name='TagScreening',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255, unique=True)),
                ('description', models.TextField(default='')),
                ('color', models.CharField(default='#FFFFFF', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='Questionary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255, unique=True)),
                ('description', models.TextField(default='')),
                ('categories', models.ManyToManyField(blank=True, to='screening.questionarycategory')),
                ('tags', models.ManyToManyField(blank=True, to='screening.tagscreening')),
            ],
            options={
                'verbose_name': 'Questionary',
                'verbose_name_plural': 'Questionaries',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='QuestionaryDimensionValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(default=0)),
                ('dimension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dimension_values', to='screening.questionarydimension')),
            ],
            options={
                'verbose_name': 'Value',
                'verbose_name_plural': 'Q - Values',
                'ordering': ('value',),
            },
        ),
        migrations.CreateModel(
            name='QuestionaryQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255)),
                ('text', models.TextField(default='')),
                ('weight', models.FloatField(default=1.0)),
                ('questionary', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='screening.questionary')),
            ],
            options={
                'verbose_name': 'Question',
                'verbose_name_plural': 'Q - Questions',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='QuestionaryAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255)),
                ('values', models.ManyToManyField(blank=True, to='screening.questionarydimensionvalue')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='screening.questionaryquestion')),
            ],
            options={
                'verbose_name': 'Answer',
                'verbose_name_plural': 'Q - Answers',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='QuestionaryResponse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_public', models.BooleanField(default=False)),
                ('is_public_expert', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='responses', to='accounts.clientprofile')),
                ('questionary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='screening.questionary')),
            ],
            options={
                'verbose_name': 'Response',
                'verbose_name_plural': 'Q - Responses',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='QuestionaryScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255)),
                ('description', models.TextField(default='')),
                ('min_score', models.FloatField(default=0)),
                ('max_score', models.FloatField(default=100)),
                ('dimension', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='screening.questionarydimension')),
                ('questionary', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='screening.questionary')),
            ],
            options={
                'verbose_name': 'Score',
                'verbose_name_plural': 'Q - Scores',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='QuestionaryScoreExtra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255)),
                ('description', models.TextField(default='')),
                ('questionary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='score_extras', to='screening.questionary')),
                ('scores', models.ManyToManyField(blank=True, to='screening.questionaryscore')),
            ],
            options={
                'verbose_name': 'Score Extra',
                'verbose_name_plural': 'Q - Score Extras',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255, unique=True)),
                ('description', models.TextField(default='')),
                ('categories', models.ManyToManyField(blank=True, to='screening.surveycategory')),
                ('tags', models.ManyToManyField(blank=True, to='screening.tagscreening')),
            ],
            options={
                'verbose_name': 'Survey',
                'verbose_name_plural': 'Surveys',
            },
        ),
        migrations.CreateModel(
            name='SurveyResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='survey_entries', to='accounts.clientprofile')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='screening.survey')),
            ],
            options={
                'verbose_name': 'Result',
                'verbose_name_plural': 'S - Results',
            },
        ),
        migrations.CreateModel(
            name='SurveyTheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255)),
                ('description', models.TextField(default='')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='themes', to='screening.survey')),
            ],
            options={
                'verbose_name': 'Theme',
                'verbose_name_plural': 'S - Themes',
            },
        ),
        migrations.CreateModel(
            name='SurveyEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='screening.surveyresult')),
                ('theme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='screening.surveytheme')),
            ],
            options={
                'verbose_name': 'Entry',
                'verbose_name_plural': 'S - Entries',
            },
        ),
        migrations.AddIndex(
            model_name='questionarydimensionvalue',
            index=models.Index(fields=['dimension'], name='screening_q_dimensi_3b0518_idx'),
        ),
        migrations.AddConstraint(
            model_name='questionarydimensionvalue',
            constraint=models.UniqueConstraint(fields=('dimension', 'value'), name='unique_dimension_value'),
        ),
        migrations.AddIndex(
            model_name='questionaryquestion',
            index=models.Index(fields=['questionary'], name='screening_q_questio_8272f2_idx'),
        ),
        migrations.AddConstraint(
            model_name='questionaryquestion',
            constraint=models.UniqueConstraint(fields=('questionary', 'title'), name='unique_question_per_questionary'),
        ),
        migrations.AddIndex(
            model_name='questionaryanswer',
            index=models.Index(fields=['question'], name='screening_q_questio_e6a6d1_idx'),
        ),
        migrations.AddConstraint(
            model_name='questionaryanswer',
            constraint=models.UniqueConstraint(fields=('question', 'title'), name='unique_answer_per_question'),
        ),
        migrations.AddIndex(
            model_name='questionaryresponse',
            index=models.Index(fields=['client', 'questionary'], name='screening_q_client__7e2d23_idx'),
        ),
        migrations.AddIndex(
            model_name='questionaryscore',
            index=models.Index(fields=['questionary', 'dimension'], name='screening_q_questio_36108e_idx'),
        ),
        migrations.AddConstraint(
            model_name='questionaryscore',
            constraint=models.UniqueConstraint(fields=('questionary', 'dimension', 'title'), name='unique_score_per_questionary_dimension'),
        ),
        migrations.AddIndex(
            model_name='questionaryscoreextra',
            index=models.Index(fields=['questionary'], name='screening_q_questio_f3c620_idx'),
        ),
        migrations.AddIndex(
            model_name='surveyresult',
            index=models.Index(fields=['client', 'survey'], name='screening_s_client__c4944e_idx'),
        ),
        migrations.AddIndex(
            model_name='surveytheme',
            index=models.Index(fields=['survey'], name='screening_s_survey__4e36d3_idx'),
        ),
        migrations.AddConstraint(
            model_name='surveytheme',
            constraint=models.UniqueConstraint(fields=('survey', 'title'), name='unique_theme_per_survey'),
        ),
        migrations.AddIndex(
            model_name='surveyentry',
            index=models.Index(fields=['theme', 'result'], name='screening_s_theme_i_095339_idx'),
        ),
        migrations.AddConstraint(
            model_name='surveyentry',
            constraint=models.UniqueConstraint(fields=('theme', 'result'), name='unique_entry_per_theme_result'),
        ),
    ]
