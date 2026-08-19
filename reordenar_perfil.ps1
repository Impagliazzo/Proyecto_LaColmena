# Script para reordenar secciones del perfil
# Mover Perfil de Búsqueda antes de Estadísticas

$lines = Get-Content "usuarios\templates\usuarios\perfil.html"
$newLines = @()

# Copiar desde el inicio hasta antes de Estadísticas (línea 299)
for ($i = 0; $i -lt 299; $i++) {
    $newLines += $lines[$i]
}

# Agregar sección de Perfil de Búsqueda (líneas 356-470)
for ($i = 356; $i -le 470; $i++) {
    $newLines += $lines[$i]
}

# Agregar sección de Estadísticas del Propietario (líneas 299-355)
for ($i = 299; $i -le 355; $i++) {
    $newLines += $lines[$i]
}

# Copiar el resto del archivo (desde línea 471 en adelante)
for ($i = 471; $i -lt $lines.Length; $i++) {
    $newLines += $lines[$i]
}

# Guardar el archivo
$newLines | Set-Content "usuarios\templates\usuarios\perfil.html"

Write-Host "✓ Perfil de Búsqueda movido antes de Estadísticas del Propietario"
