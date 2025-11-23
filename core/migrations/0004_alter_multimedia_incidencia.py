                                               

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_encuesta_prioridad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multimedia',
            name='incidencia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='multimedias', to='core.incidencia'),
        ),
    ]
