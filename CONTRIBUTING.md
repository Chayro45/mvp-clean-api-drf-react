# Contributing to Minimum API

¡Gracias por tu interés en contribuir! Este documento proporciona guías para contribuir al proyecto.

---

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Features](#sugerir-features)
- [Pull Requests](#pull-requests)
- [Convenciones de Código](#convenciones-de-código)
- [Commits](#commits)
- [Desarrollo Local](#desarrollo-local)

---

## 📜 Código de Conducta

Este proyecto adhiere al [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Al participar, se espera que respetes este código.

### Nuestros Estándares

**Comportamientos que fomentan un ambiente positivo:**
- Uso de lenguaje acogedor e inclusivo
- Respeto a puntos de vista y experiencias diferentes
- Aceptar críticas constructivas con gracia
- Enfocarse en lo que es mejor para la comunidad
- Mostrar empatía hacia otros miembros

**Comportamientos inaceptables:**
- Uso de lenguaje o imágenes sexualizadas
- Trolling, comentarios insultantes o ataques personales
- Acoso público o privado
- Publicar información privada de otros sin permiso
- Otra conducta que razonablemente se considere inapropiada

---

## 🤝 Cómo Contribuir

### Formas de Contribuir

1. **Reportar bugs** - Ayuda a mejorar la calidad
2. **Sugerir features** - Comparte ideas de mejora
3. **Mejorar documentación** - Siempre necesita amor
4. **Escribir código** - Arreglar bugs o agregar features
5. **Revisar PRs** - Ayuda a mantener calidad del código
6. **Responder issues** - Ayuda a la comunidad

---

## 🐛 Reportar Bugs

Antes de crear un bug report:

1. **Busca en issues existentes** - Quizás ya fue reportado
2. **Verifica que sea reproducible** - Asegúrate de poder replicarlo
3. **Prueba con la última versión** - Puede estar ya arreglado

### Cómo Reportar

Crea un issue con esta información:

**Título**: Descripción breve del problema

**Template**:
```markdown
## Descripción
[Descripción clara del bug]

## Pasos para Reproducir
1. Ir a '...'
2. Click en '...'
3. Scroll hasta '...'
4. Ver error

## Comportamiento Esperado
[Qué debería pasar]

## Comportamiento Actual
[Qué pasa realmente]

## Screenshots
[Si aplica, agregar screenshots]

## Ambiente
- OS: [ej. macOS 13.0]
- Browser: [ej. Chrome 120]
- Versión del Proyecto: [ej. 1.0.0]
- Docker: [Sí/No, versión]

## Logs/Errores
```
[Pegar logs relevantes]
```

## Contexto Adicional
[Cualquier otro contexto útil]
```

---

## ✨ Sugerir Features

### Antes de Sugerir

1. **Verifica el roadmap** - Puede estar ya planeado
2. **Busca sugerencias similares** - Evita duplicados
3. **Considera el alcance** - Debe alinearse con los objetivos del proyecto

### Cómo Sugerir

**Template**:
```markdown
## Feature Request

### Problema que Resuelve
[Describe el problema o necesidad]

### Solución Propuesta
[Describe cómo funcionaría el feature]

### Alternativas Consideradas
[Otras soluciones que consideraste]

### Contexto Adicional
[Screenshots, mockups, ejemplos de otros proyectos]

### Impacto
- [ ] Backend
- [ ] Frontend
- [ ] DevOps
- [ ] Documentación

### Prioridad
- [ ] Critical
- [ ] High
- [ ] Medium
- [ ] Low
```

---

## 🔀 Pull Requests

### Proceso

1. **Fork el repositorio**
2. **Crea una rama** desde `main`:
   ```bash
   git checkout -b feature/nombre-descriptivo
   ```
3. **Haz tus cambios**
4. **Agrega tests** (si aplica)
5. **Ejecuta tests**:
   ```bash
   make test
   make lint
   ```
6. **Commit** siguiendo convenciones
7. **Push** a tu fork
8. **Abre PR** al repositorio original

### Checklist del PR

- [ ] Código sigue las convenciones del proyecto
- [ ] Tests agregados/actualizados
- [ ] Todos los tests pasan
- [ ] Documentación actualizada (si aplica)
- [ ] Commits siguen formato convencional
- [ ] PR tiene descripción clara
- [ ] Screenshots agregados (para cambios de UI)

### Template del PR

```markdown
## Descripción

[Descripción clara de los cambios]

## Tipo de Cambio

- [ ] Bug fix (cambio que arregla un issue)
- [ ] New feature (cambio que agrega funcionalidad)
- [ ] Breaking change (cambio que rompe compatibilidad)
- [ ] Documentación

## ¿Cómo se Ha Testeado?

[Describe las pruebas que ejecutaste]

- [ ] Backend tests pasan
- [ ] Frontend tests pasan
- [ ] Probado localmente
- [ ] Probado en Docker

## Screenshots (si aplica)

[Agregar screenshots de cambios visuales]

## Checklist

- [ ] Mi código sigue las guías de estilo
- [ ] He revisado mi propio código
- [ ] He comentado código complejo
- [ ] He actualizado la documentación
- [ ] Mis cambios no generan warnings
- [ ] He agregado tests
- [ ] Todos los tests pasan
- [ ] He actualizado CHANGELOG.md
```

---

## 💻 Convenciones de Código

### Python (Backend)

```python
# Seguir PEP 8
# Usar black para formatear
black apps/

# Nombres
def calculate_total_amount():  # snake_case
    MAX_RETRIES = 3  # UPPER_SNAKE_CASE
    user_count = 10  # snake_case
    
class UserService:  # PascalCase
    pass

# Docstrings
def create_user(username, email):
    """
    Crea un nuevo usuario.
    
    Args:
        username (str): Nombre de usuario
        email (str): Email del usuario
    
    Returns:
        User: Usuario creado
    """
    pass
```

### JavaScript (Frontend)

```javascript
// Nombres
const calculateTotal = () => {};  // camelCase
const MAX_ITEMS = 100;  // UPPER_SNAKE_CASE

const UserCard = () => {};  // PascalCase (componentes)

// JSDoc
/**
 * Calcula el total de items
 * @param {number[]} prices - Array de precios
 * @returns {number} Total calculado
 */
const calculateTotal = (prices) => {
  return prices.reduce((sum, price) => sum + price, 0);
};
```

### CSS/Tailwind

```css
/* Utility classes preferidas sobre CSS custom */

/* Evitar */
.my-custom-button {
  padding: 1rem;
  background-color: blue;
  border-radius: 0.5rem;
}

/* Preferir */
<button className="px-4 py-2 bg-blue-500 rounded-lg">
```

---

## 📝 Commits

### Formato

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<scope>): <descripción>

[cuerpo opcional]

[footer opcional]
```

### Tipos

- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formato (sin cambiar lógica)
- `refactor`: Refactorización de código
- `test`: Agregar/modificar tests
- `chore`: Tareas de mantenimiento

### Ejemplos

```bash
feat(users): agregar endpoint de cambio de password

fix(auth): corregir auto-refresh de JWT cuando expira

docs(api): actualizar documentación de endpoints

test(users): agregar tests de UserService

refactor(frontend): extraer lógica de auth a custom hook

chore(deps): actualizar Django a 4.2.10
```

### Scope

Opciones comunes:
- `users`, `auth`, `core` (apps del backend)
- `frontend`, `backend`
- `api`, `ui`, `docs`
- `ci`, `docker`, `deps`

---

## 🛠️ Desarrollo Local

### Setup Inicial

```bash
# Clonar tu fork
git clone https://github.com/tu-usuario/minimum-api.git
cd minimum-api

# Agregar upstream
git remote add upstream https://github.com/original-usuario/minimum-api.git

# Crear rama
git checkout -b feature/mi-feature

# Instalar y levantar
make install
```

### Workflow Diario

```bash
# Actualizar main
git checkout main
git pull upstream main

# Crear/actualizar rama
git checkout feature/mi-feature
git rebase main

# Hacer cambios...

# Commit
git add .
git commit -m "feat(users): descripción"

# Push a tu fork
git push origin feature/mi-feature
```

### Ejecutar Tests

```bash
# Backend
make test

# Frontend
make test-frontend

# Linting
make lint

# Todo junto
make test && make test-frontend && make lint
```

---

## 🔍 Revisión de Código

### Como Autor

- Responde a comentarios constructivamente
- Realiza cambios solicitados
- Marca conversaciones como resueltas
- Sé paciente con el proceso

### Como Revisor

- Sé constructivo y cortés
- Sugiere mejoras específicas
- Explica el "por qué"
- Aprecia el esfuerzo del autor
- Aprueba cuando esté listo

---

## ❓ Preguntas

Si tienes preguntas sobre cómo contribuir:

1. Revisa la documentación en `/docs`
2. Busca en issues cerrados
3. Abre un nuevo issue con etiqueta `question`
4. Únete a las discusiones de GitHub

---

## 📄 Licencia

Al contribuir, aceptas que tus contribuciones serán licenciadas bajo la misma licencia del proyecto (MIT).

---

## 🙏 Reconocimientos

¡Gracias a todos los contribuidores que han ayudado a mejorar este proyecto!

<!-- Lista de contribuidores se genera automáticamente -->

---

¿Tienes más preguntas? Abre un issue o inicia una discusión en GitHub.

**¡Happy coding! 🚀**
