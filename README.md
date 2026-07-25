# Sistema Experto — Recomendador de Cultivos Agrícolas (Colombia)

> Esta es la documentación de la versión **de archivo único**
> (`motor_inferencia_cultivos.py`), previa a la modularización del
> proyecto en el paquete `sistema_experto_cultivos/`.

Sistema experto que recomienda el cultivo mejor adaptado a un perfil de
usuario (región, altitud, pH del suelo, clima y presupuesto), usando un
motor de inferencia por **matching multicriterio ponderado** (forward
chaining con reglas de compatibilidad, no reglas booleanas rígidas).

## Cultivos en la base de conocimiento

Aguacate Hass · Mango Tommy · Café · Cacao · Plátano · Banano · Fresa ·
Papa · Yuca · Guanábana

## Archivo

```
motor_inferencia_cultivos.py
```

Todo el sistema vive en un único archivo, organizado en 4 secciones
internas (marcadas con comentarios en el código):

| Sección | Contenido |
|---|---|
| 1. Base de conocimiento | `BASE_CONOCIMIENTO`: lista con el perfil de cada cultivo (región, msnm, pH, clima, presupuesto, rentabilidad, cuidados) |
| 2. Base de hechos | `HechosUsuario`: `dataclass` con los datos que declara el usuario |
| 3. Motor de inferencia | Clase `MotorInferencia`: reglas por variable, cálculo del ranking y explicación en lenguaje natural |
| 4. Interfaz de consola | Función `main()`: hace las preguntas por `input()` y muestra el resultado |

## Cómo ejecutarlo

```bash
python3 motor_inferencia_cultivos.py
```

El programa pregunta, en orden: región, altitud (msnm), pH del suelo,
clima (Frío/Templado/Cálido), presupuesto por hectárea (millones de
COP) y tipo de terreno (opcional). Al final muestra:

- El cultivo con mayor compatibilidad, con el desglose por variable.
- Inversión estimada, tiempo hasta la primera cosecha, rentabilidad y
  cuidados de ese cultivo.
- Las siguientes 3 opciones más compatibles.

También guarda el resultado completo en `resultado_recomendacion.json`,
para poder reutilizarlo desde otra aplicación.

## Cómo funciona el motor (resumen)

Por cada cultivo se calcula un puntaje 0-100 en cinco variables y se
combinan con pesos fijos definidos en el diccionario `PESOS`:

```python
PESOS = {
    "msnm": 0.25,
    "ph": 0.20,
    "clima": 0.20,
    "presupuesto": 0.20,
    "region": 0.15,
}
```

```
compatibilidad = (msnm × 0.25) + (ph × 0.20) + (clima × 0.20)
                + (presupuesto × 0.20) + (region × 0.15)
```

**Reglas por variable** (método `MotorInferencia._regla_*`):

- **Altitud y pH** (`_regla_rango`): 100% si el valor del usuario cae
  dentro del rango óptimo del cultivo; si no, se penaliza
  proporcionalmente a la distancia, hasta llegar a 0%.
- **Clima** (`_regla_clima`): 100% si el clima declarado está entre los
  climas aptos del cultivo; si no, 30% (compatibilidad parcial, no se
  descarta del todo).
- **Presupuesto** (`_regla_presupuesto`): 100% si el presupuesto alcanza
  el mínimo requerido; si no, un porcentaje proporcional a cuánto del
  mínimo se cubre.
- **Región** (`_regla_region`): 100% si coincide (o coincide
  parcialmente el nombre) con alguna región conocida del cultivo; si
  no, 40%.

**Orden del ranking** (`MotorInferencia.inferir`): descendente por
compatibilidad; en caso de empate, se prioriza el cultivo con menor
presupuesto mínimo requerido (el más accesible).

**Explicación** (`MotorInferencia.explicar`): traduce el detalle
numérico a una frase legible, por ejemplo *"altitud ideal (100%); pH
del suelo poco favorable (45%)"*.

## Limitaciones de esta versión

Comparado con la versión modular final (`sistema_experto_cultivos/`),
esta versión de archivo único **no incluye**:

- Indicador de confianza por recomendación.
- Análisis de sensibilidad de los pesos.
- Corrección de errores de tipeo en la región.
- Nivel de riesgo por cultivo.
- Sugerencia de diversificación de cultivos.
- Historial persistente de consultas.
- Exportación a CSV o TXT (solo exporta a JSON).
- Modo no interactivo por argumentos de línea de comandos.
- Validación de datos de entrada (si se ingresa un pH fuera de rango
  razonable, el programa lo acepta igual).

Esas funciones se agregaron justamente al pasar a la versión modular.

## Ejemplo de ejecución

```
Región o departamento donde cultivarás: Antioquia
Altitud del terreno (msnm): 1800
pH del suelo (ej. 5.8): 5.6
Clima predominante en la zona:
  1. Frío
  2. Templado
  3. Cálido
Elige una opción (número): 2
Presupuesto disponible por hectárea (millones de COP): 20
Tipo de terreno (opcional, ej. ladera, plano, ondulado): ladera

==================================================================
 RECOMENDACIÓN PRINCIPAL: Café (100.0% de compatibilidad)
==================================================================

Por qué encaja: altitud ideal (100.0%); pH del suelo ideal (100.0%);
clima ideal (100.0%); presupuesto ideal (100.0%); región ideal (100.0%)
```


