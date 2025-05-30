# Generated by Django 5.2.1 on 2025-05-29 06:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryQuestionary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=255)),
                ('description', models.TextField(default='')),
            ],
            options={
                'verbose_name': 'Questionary Category',
                'verbose_name_plural': 'Questionary Categories',
            },
        ),
        migrations.CreateModel(
            name='CategorySurvey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=255)),
                ('description', models.TextField(default='')),
            ],
            options={
                'verbose_name': 'Questionary Category',
                'verbose_name_plural': 'Questionary Categories',
            },
        ),
        migrations.CreateModel(
            name='QuestionaryDimension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=255)),
                ('description', models.TextField(default='')),
            ],
            options={
                'verbose_name': 'Questionary Dimension',
                'verbose_name_plural': 'Questionary Dimensions',
            },
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255, unique=True)),
                ('description', models.TextField(default='')),
            ],
            options={
                'verbose_name': 'Survey',
                'verbose_name_plural': 'Surveys',
            },
        ),
        migrations.CreateModel(
            name='Questionary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, default='', max_length=255, unique=True)),
                ('description', models.TextField(default='')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questionaries', to='screening.categoryquestionary')),
            ],
            options={
                'verbose_name': 'Questionary',
                'verbose_name_plural': 'Questionaries',
            },
        ),
        migrations.CreateModel(
            name='QuestionaryQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=255)),
                ('text', models.TextField(default='')),
                ('weight', models.FloatField(default=1.0)),
                ('questionary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='screening.questionary')),
            ],
            options={
                'verbose_name': 'Questionary Question',
                'verbose_name_plural': 'Questionary Questions',
            },
        ),
        migrations.CreateModel(
            name='QuestionaryAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=255)),
                ('value', models.FloatField()),
                ('dimension', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='screening.questionarydimension')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='screening.questionaryquestion')),
            ],
            options={
                'verbose_name': 'Questionary Answer',
                'verbose_name_plural': 'Questionary Answers',
            },
        ),
        migrations.CreateModel(
            name='QuestionaryResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=128)),
                ('description', models.TextField(default='')),
                ('questionary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='results', to='screening.questionary')),
            ],
            options={
                'verbose_name': 'Questionary Result',
                'verbose_name_plural': 'Questionary Results',
            },
        ),
        migrations.CreateModel(
            name='QuestionaryResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_public', models.BooleanField(default=False)),
                ('is_public_expert', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('answers', models.ManyToManyField(blank=True, related_name='responses', to='screening.questionaryanswer')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='questionary_results', to='accounts.clientprofile')),
                ('questionary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='screening.questionary')),
                ('result', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='screening.questionaryresult')),
            ],
            options={
                'verbose_name': 'Questionary Response',
                'verbose_name_plural': 'Questionary Responses',
            },
        ),
        migrations.CreateModel(
            name='QuestionaryScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=255)),
                ('min_score', models.FloatField(default=0)),
                ('max_score', models.FloatField(default=100)),
                ('dimension', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='results', to='screening.questionarydimension')),
            ],
            options={
                'verbose_name': 'Questionary Score',
                'verbose_name_plural': 'Questionary Scores',
            },
        ),
        migrations.AddField(
            model_name='questionaryresult',
            name='scores',
            field=models.ManyToManyField(related_name='results', to='screening.questionaryscore'),
        ),
        migrations.CreateModel(
            name='SurveyResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='survey_entries', to='accounts.clientprofile')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='screening.survey')),
            ],
            options={
                'verbose_name': 'Survey Result',
                'verbose_name_plural': 'Survey Results',
            },
        ),
        migrations.CreateModel(
            name='SurveyTheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=255)),
                ('description', models.TextField(default='')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='themes', to='screening.survey')),
            ],
            options={
                'verbose_name': 'Survey Theme',
                'verbose_name_plural': 'Survey Themes',
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
                'verbose_name': 'Survey Entry',
                'verbose_name_plural': 'Survey Entries',
            },
        ),
        migrations.AddIndex(
            model_name='questionaryanswer',
            index=models.Index(fields=['question', 'dimension'], name='screening_q_questio_000f49_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='questionaryanswer',
            unique_together={('question', 'dimension')},
        ),
        migrations.AddIndex(
            model_name='surveyresult',
            index=models.Index(fields=['client', 'survey'], name='screening_s_client__c4944e_idx'),
        ),
        migrations.AddIndex(
            model_name='surveyentry',
            index=models.Index(fields=['theme', 'result'], name='screening_s_theme_i_095339_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='surveyentry',
            unique_together={('theme', 'result')},
        ),
    ]
