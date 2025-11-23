                                               

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='multimedia',
            options={'ordering': ['-creadoEl'], 'verbose_name': 'Evidencia Multimedia', 'verbose_name_plural': 'Evidencias Multimedia'},
        ),
        migrations.RemoveField(
            model_name='multimedia',
            name='url',
        ),
        migrations.AddField(
            model_name='multimedia',
            name='archivo',
            field=models.FileField(default='', upload_to='evidencias/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'mpeg', 'avi', 'mov', 'mp3', 'wav', 'ogg', 'm4a', 'pdf', 'doc', 'docx', 'txt'])]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='multimedia',
            name='encuesta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='evidencias', to='core.encuesta'),
        ),
        migrations.AddField(
            model_name='multimedia',
            name='tamanio',
            field=models.IntegerField(blank=True, help_text='Tamaño en bytes', null=True),
        ),
        migrations.AlterField(
            model_name='multimedia',
            name='tipo',
            field=models.CharField(choices=[('imagen', 'Imagen'), ('video', 'Video'), ('audio', 'Audio'), ('documento', 'Documento'), ('otro', 'Otro')], max_length=50),
        ),
    ]
