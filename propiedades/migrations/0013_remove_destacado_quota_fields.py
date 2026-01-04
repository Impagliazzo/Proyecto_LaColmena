# Generated manually to remove quota system fields

from django.db import migrations


def recreate_destacado_table(apps, schema_editor):
    """
    SQLite no soporta DROP COLUMN, así que recreamos la tabla sin los campos del sistema de cupos
    """
    # Primero, eliminar registros huérfanos sin propiedad_id
    schema_editor.execute("DELETE FROM propiedades_destacado WHERE propiedad_id IS NULL;")
    
    # Crear tabla temporal con la estructura correcta (sin campos de cupos)
    schema_editor.execute("""
        CREATE TABLE propiedades_destacado_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo VARCHAR(20) NOT NULL,
            duracion_dias INTEGER NOT NULL,
            precio_pagado DECIMAL NOT NULL,
            fecha_inicio DATETIME NOT NULL,
            fecha_fin DATETIME NOT NULL,
            fecha_compra DATETIME NOT NULL,
            activo BOOLEAN NOT NULL,
            propiedad_id BIGINT NOT NULL REFERENCES propiedades_propiedad(id) DEFERRABLE INITIALLY DEFERRED
        );
    """)
    
    # Copiar datos existentes (solo los campos que queremos mantener)
    schema_editor.execute("""
        INSERT INTO propiedades_destacado_new 
        (id, tipo, duracion_dias, precio_pagado, fecha_inicio, fecha_fin, fecha_compra, activo, propiedad_id)
        SELECT id, tipo, duracion_dias, precio_pagado, fecha_inicio, fecha_fin, fecha_compra, activo, propiedad_id
        FROM propiedades_destacado;
    """)
    
    # Eliminar tabla vieja
    schema_editor.execute("DROP TABLE propiedades_destacado;")
    
    # Renombrar tabla nueva
    schema_editor.execute("ALTER TABLE propiedades_destacado_new RENAME TO propiedades_destacado;")
    
    # Recrear índices
    schema_editor.execute("""
        CREATE INDEX propiedades_destacado_propiedad_id_idx 
        ON propiedades_destacado (propiedad_id);
    """)


class Migration(migrations.Migration):

    dependencies = [
        ('propiedades', '0012_alter_propiedad_titulo'),
    ]

    operations = [
        migrations.RunPython(recreate_destacado_table, reverse_code=migrations.RunPython.noop),
    ]
