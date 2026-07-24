
"""
Sistema experto para recomendación de cultivos agrícolas en Colombia
=====================================================================
 
Motor de inferencia basado en matching multicriterio ponderado.
 
Dado el perfil del usuario (región, msnm, clima, pH del suelo y
presupuesto disponible por hectárea), el motor evalúa 10 cultivos
candidatos y entrega:
 
    - El cultivo mejor adaptado a las condiciones declaradas.
    - Su porcentaje de compatibilidad y el detalle por variable.
    - Qué tan rentable es (cualitativo, con contexto de mercado).
    - Los cuidados y exigencias que conlleva mantenerlo.
 
Cultivos disponibles en la base de conocimiento:
    Aguacate Hass, Mango Tommy, Café, Cacao, Plátano, Banano,
    Fresa, Papa, Yuca, Guanábana.
 
Estructura del archivo:
    1. Base de conocimiento (BASE_CONOCIMIENTO)
    2. Base de hechos (HechosUsuario)
    3. Motor de inferencia (clase MotorInferencia)
    4. Interfaz de consola (main)
"""
 
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json
 
 
# ---------------------------------------------------------------------------
# 1. BASE DE CONOCIMIENTO
# ---------------------------------------------------------------------------
# Cada cultivo es un perfil de requisitos agronómicos, económicos y de
# manejo. Los rangos (msnm, ph) representan las condiciones óptimas; el
# motor calcula qué tan lejos está el usuario de esos rangos, no solo si
# "cae dentro" o no.
 
BASE_CONOCIMIENTO: List[Dict] = [
    {
        "nombre": "Aguacate Hass",
        "regiones": ["Antioquia", "Caldas", "Risaralda", "Quindío",
                     "Tolima", "Valle del Cauca", "Cauca"],
        "msnm": (1600, 2400),
        "ph": (5.5, 6.5),
        "clima": ["Frío", "Templado"],
        "presupuesto_min_millones": 20,
        "presupuesto_max_millones": 30,
        "primera_cosecha_anios": "3 a 5",
        "rentabilidad": "Alta. Fuerte demanda internacional (EE. UU. y "
                         "Europa) y precio estable de exportación; puede "
                         "producir hasta 20-30 años con buen manejo. La "
                         "desventaja es la alta inversión inicial y la "
                         "demora en dar el primer fruto.",
        "cuidados": "Cero tolerancia al encharcamiento (Phytophthora "
                    "cinnamomi); nutrición foliar fina (boro, zinc, "
                    "calcio); podas de luz; registro ICA si es para "
                    "exportación.",
    },
    {
        "nombre": "Mango Tommy",
        "regiones": ["Tolima", "Magdalena", "Cundinamarca", "Antioquia",
                     "Atlántico", "Cesar"],
        "msnm": (0, 1000),
        "ph": (5.6, 7.0),
        "clima": ["Cálido"],
        "presupuesto_min_millones": 10,
        "presupuesto_max_millones": 15,
        "primera_cosecha_anios": "3 a 4",
        "rentabilidad": "Media-alta. Es una de las variedades de mayor "
                         "demanda de exportación; rendimientos promedio de "
                         "10-16 ton/ha en cultivos maduros. El retorno "
                         "mejora notablemente después del año 4.",
        "cuidados": "Necesita una época seca definida para inducir "
                    "floración; buena radiación solar y baja humedad "
                    "relativa; control estricto de mosca de la fruta y "
                    "antracnosis.",
    },
    {
        "nombre": "Café",
        "regiones": ["Huila", "Antioquia", "Caldas", "Quindío", "Risaralda",
                     "Cauca", "Nariño", "Santander"],
        "msnm": (1200, 2000),
        "ph": (5.0, 5.8),
        "clima": ["Templado", "Frío"],
        "presupuesto_min_millones": 15,
        "presupuesto_max_millones": 22,
        "primera_cosecha_anios": "2 a 3",
        "rentabilidad": "Media-alta. Mercado global consolidado; posibilidad "
                         "de precios premium si es café especial u orgánico. "
                         "Requiere inversión constante en mano de obra para "
                         "la recolección selectiva anual.",
        "cuidados": "Recolección manual selectiva muy intensiva en mano de "
                    "obra; monitoreo constante de roya y broca; "
                    "fertilización 2-3 veces al año.",
    },
    {
        "nombre": "Cacao",
        "regiones": ["Santander", "Antioquia", "Arauca", "Huila", "Tolima", "Nariño"],
        "msnm": (0, 1200),
        "ph": (6.0, 7.0),
        "clima": ["Cálido"],
        "presupuesto_min_millones": 12,
        "presupuesto_max_millones": 16,
        "primera_cosecha_anios": "2 a 3",
        "rentabilidad": "Alta y en crecimiento por la demanda global de "
                         "chocolate y derivados; se puede combinar con "
                         "sistemas agroforestales para ingresos adicionales, "
                         "pero es vulnerable a enfermedades si el manejo "
                         "fitosanitario falla.",
        "cuidados": "Requiere sistema agroforestal con sombrío (plátano o "
                    "maderables); podas rigurosas contra monilia y escoba "
                    "de bruja.",
    },
    {
        "nombre": "Plátano",
        "regiones": ["Quindío", "Risaralda", "Caldas", "Tolima",
                     "Cundinamarca", "Meta", "Arauca"],
        "msnm": (0, 1800),
        "ph": (5.5, 7.0),
        "clima": ["Cálido", "Templado"],
        "presupuesto_min_millones": 10,
        "presupuesto_max_millones": 15,
        "primera_cosecha_anios": "0.8 a 1",
        "rentabilidad": "Media. Demanda interna constante y ciclo corto "
                         "(primera cosecha antes del año), lo que da flujo "
                         "de caja más rápido que los frutales perennes.",
        "cuidados": "Deshoje, desmache y apuntalado para evitar caída por "
                    "viento; control constante de sigatoka negra y "
                    "fusarium raza 4 tropical.",
    },
    {
        "nombre": "Banano",
        "regiones": ["Antioquia (Urabá)", "Magdalena"],
        "msnm": (0, 1000),
        "ph": (5.8, 7.2),
        "clima": ["Cálido"],
        "presupuesto_min_millones": 15,
        "presupuesto_max_millones": 20,
        "primera_cosecha_anios": "0.8 a 1",
        "rentabilidad": "Alta si se orienta a exportación (Colombia es uno "
                         "de los mayores exportadores mundiales), pero exige "
                         "más inversión en infraestructura de empaque y "
                         "logística que el plátano de consumo local.",
        "cuidados": "Embolsado de racimo, deshoje y amarrado; control "
                    "constante de sigatoka negra y fusarium raza 4 "
                    "tropical; alta exigencia de agua y nutrición.",
    },
    {
        "nombre": "Fresa",
        "regiones": ["Cundinamarca", "Boyacá", "Antioquia"],
        "msnm": (1800, 2800),
        "ph": (5.8, 6.5),
        "clima": ["Frío"],
        "presupuesto_min_millones": 40,
        "presupuesto_max_millones": 60,
        "primera_cosecha_anios": "0.3 a 0.5",
        "rentabilidad": "Alta pero de ciclo corto: genera ingresos en pocos "
                         "meses y tiene alta demanda en supermercados, "
                         "heladerías y exportación, aunque exige la mayor "
                         "inversión inicial por hectárea de todo el listado.",
        "cuidados": "Fertirriego por goteo constante; acolchado plástico "
                    "(mulching); deshierbe y recolección casi diaria en "
                    "temporada; protección contra botrytis y ácaros.",
    },
    {
        "nombre": "Papa",
        "regiones": ["Cundinamarca", "Boyacá", "Nariño", "Antioquia"],
        "msnm": (2000, 3100),
        "ph": (5.0, 6.0),
        "clima": ["Frío"],
        "presupuesto_min_millones": 18,
        "presupuesto_max_millones": 24,
        "primera_cosecha_anios": "0.3 a 0.5",
        "rentabilidad": "Media. Mercado interno amplio y estable, pero con "
                         "alta volatilidad de precios y altos costos de "
                         "fertilizantes y fungicidas por ciclo.",
        "cuidados": "Alta demanda de fertilizantes NPK y fungicidas cada "
                    "8-10 días contra la gota (Phytophthora); reaporque "
                    "manual o mecánico.",
    },
    {
        "nombre": "Yuca",
        "regiones": ["Bolívar", "Sucre", "Córdoba", "Magdalena"],
        "msnm": (0, 1200),
        "ph": (5.5, 7.0),
        "clima": ["Cálido"],
        "presupuesto_min_millones": 4.5,
        "presupuesto_max_millones": 7,
        "primera_cosecha_anios": "0.7 a 1",
        "rentabilidad": "Baja-media en valor por hectárea, pero es la "
                         "opción de menor riesgo e inversión de todo el "
                         "listado: rústica y resistente a sequías, ideal "
                         "para presupuestos limitados.",
        "cuidados": "Muy rústico; requiere sobre todo buena preparación del "
                    "suelo para facilitar el arranque de la raíz en cosecha.",
    },
    {
        "nombre": "Guanábana",
        "regiones": ["Tolima", "Huila", "Magdalena", "Valle del Cauca",
                     "Meta", "Antioquia", "Córdoba", "Cesar", "Santander",
                     "Cundinamarca"],
        "msnm": (0, 1200),
        "ph": (5.5, 6.5),
        "clima": ["Cálido"],
        "presupuesto_min_millones": 25,
        "presupuesto_max_millones": 30,
        "primera_cosecha_anios": "2 a 3",
        "rentabilidad": "Alto potencial por ser un cultivo de nicho con "
                         "demanda creciente para pulpa y jugo (mercado de "
                         "exportación en expansión), pero es un cultivo de "
                         "riesgo y de rendimiento tardío: producción óptima "
                         "recién entre el año 4 y 6.",
        "cuidados": "Muy susceptible al frío; requiere alta luminosidad "
                    "(mínimo 10 horas/día) y buen drenaje; poda y "
                    "polinización manual para mejorar el amarre de fruto.",
    },
]
 
# Pesos por variable (deben sumar 1.0). Ajustables según criterio experto.
PESOS = {
    "msnm": 0.25,
    "ph": 0.20,
    "clima": 0.20,
    "presupuesto": 0.20,
    "region": 0.15,
}
 
# Tolerancias para variables continuas: cuánto "penaliza" alejarse del rango
# óptimo antes de llegar a 0% de compatibilidad.
TOLERANCIA_MSNM = 400   # metros
TOLERANCIA_PH = 1.0     # unidades de pH
 
 
# ---------------------------------------------------------------------------
# 2. BASE DE HECHOS
# ---------------------------------------------------------------------------
 
@dataclass
class HechosUsuario:
    """Representa la memoria de trabajo: lo que el usuario ha declarado."""
    region: str
    msnm: float
    ph: float
    clima: str           # "Frío", "Templado" o "Cálido"
    presupuesto_millones: float
    terreno: str = ""     # opcional, informativo
 
 
# ---------------------------------------------------------------------------
# 3. MOTOR DE INFERENCIA
# ---------------------------------------------------------------------------
 
class MotorInferencia:
    """
    Motor de inferencia por encadenamiento hacia adelante (forward chaining)
    con matching multicriterio ponderado.
 
    Flujo:
        hechos -> por cada cultivo, evalúa reglas de compatibilidad
               -> combina puntajes con pesos
               -> genera ranking explicado con info de rentabilidad y cuidados
    """
 
    def __init__(self, base_conocimiento: List[Dict], pesos: Dict[str, float]):
        self.base_conocimiento = base_conocimiento
        self.pesos = pesos
 
    # --- Reglas individuales (una por variable) -----------------------
 
    @staticmethod
    def _regla_rango(valor: float, rango: Tuple[float, float], tolerancia: float) -> float:
        """SI valor está dentro del rango ENTONCES 100.
        SI NO, penaliza proporcionalmente a la distancia hasta 0."""
        minimo, maximo = rango
        if minimo <= valor <= maximo:
            return 100.0
        distancia = minimo - valor if valor < minimo else valor - maximo
        return max(0.0, 100.0 - (distancia / tolerancia) * 100.0)
 
    @staticmethod
    def _regla_clima(clima_usuario: str, climas_cultivo: List[str]) -> float:
        """SI el clima declarado está en los climas aptos ENTONCES 100.
        SI NO, compatibilidad parcial baja (30)."""
        return 100.0 if clima_usuario in climas_cultivo else 30.0
 
    @staticmethod
    def _regla_presupuesto(presupuesto_usuario: float, minimo_requerido: float) -> float:
        """SI el presupuesto alcanza el mínimo ENTONCES 100.
        SI NO, proporcional a cuánto del mínimo se cubre."""
        if presupuesto_usuario >= minimo_requerido:
            return 100.0
        return max(0.0, round((presupuesto_usuario / minimo_requerido) * 100.0, 1))
 
    @staticmethod
    def _regla_region(region_usuario: str, regiones_cultivo: List[str]) -> float:
        """SI la región coincide (o coincide parcialmente el nombre) ENTONCES 100.
        SI NO, 40 (no descarta, pero penaliza: la región influye en clima y
        suelo, aunque el usuario podría estar en una subregión no listada)."""
        region_usuario_norm = region_usuario.strip().lower()
        for r in regiones_cultivo:
            if region_usuario_norm in r.lower() or r.lower() in region_usuario_norm:
                return 100.0
        return 40.0
 
    # --- Evaluación de un cultivo ---------------------------------------
 
    def evaluar_cultivo(self, cultivo: Dict, hechos: HechosUsuario) -> Dict:
        puntajes = {
            "msnm": self._regla_rango(hechos.msnm, cultivo["msnm"], TOLERANCIA_MSNM),
            "ph": self._regla_rango(hechos.ph, cultivo["ph"], TOLERANCIA_PH),
            "clima": self._regla_clima(hechos.clima, cultivo["clima"]),
            "presupuesto": self._regla_presupuesto(
                hechos.presupuesto_millones, cultivo["presupuesto_min_millones"]
            ),
            "region": self._regla_region(hechos.region, cultivo["regiones"]),
        }
 
        compatibilidad = sum(
            puntajes[var] * self.pesos[var] for var in puntajes
        )
 
        return {
            "cultivo": cultivo["nombre"],
            "compatibilidad": round(compatibilidad, 1),
            "detalle": {k: round(v, 1) for k, v in puntajes.items()},
            "primera_cosecha_anios": cultivo["primera_cosecha_anios"],
            "rentabilidad": cultivo["rentabilidad"],
            "cuidados": cultivo["cuidados"],
            "presupuesto_sugerido": (
                f"${cultivo['presupuesto_min_millones']}M - "
                f"${cultivo['presupuesto_max_millones']}M COP/ha"
            ),
        }
 
    # --- Inferencia completa (ordenamiento del ranking) -------------------
 
    def inferir(self, hechos: HechosUsuario) -> List[Dict]:
        resultados = [
            self.evaluar_cultivo(cultivo, hechos)
            for cultivo in self.base_conocimiento
        ]
        # Orden descendente por % de compatibilidad; en caso de empate,
        # se prioriza el cultivo con menor presupuesto mínimo requerido
        # (más accesible para el usuario).
        presupuestos_min = {
            c["nombre"]: c["presupuesto_min_millones"] for c in self.base_conocimiento
        }
        return sorted(
            resultados,
            key=lambda r: (r["compatibilidad"], -presupuestos_min[r["cultivo"]]),
            reverse=True,
        )
 
    def explicar(self, resultado: Dict) -> str:
        """Genera una explicación en lenguaje natural del porqué de un puntaje."""
        d = resultado["detalle"]
        partes = []
        etiquetas = {
            "msnm": "altitud", "ph": "pH del suelo", "clima": "clima",
            "presupuesto": "presupuesto", "region": "región",
        }
        for var, etiqueta in etiquetas.items():
            valor = d[var]
            if valor >= 90:
                partes.append(f"{etiqueta} ideal ({valor}%)")
            elif valor >= 60:
                partes.append(f"{etiqueta} aceptable ({valor}%)")
            else:
                partes.append(f"{etiqueta} poco favorable ({valor}%)")
        return "; ".join(partes)
 
 
# ---------------------------------------------------------------------------
# 4. INTERFAZ DE CONSOLA
# ---------------------------------------------------------------------------
 
def pedir_float(mensaje: str) -> float:
    while True:
        try:
            return float(input(mensaje).strip())
        except ValueError:
            print("  Por favor ingresa un número válido.")
 
 
def pedir_opcion(mensaje: str, opciones: List[str]) -> str:
    print(mensaje)
    for i, op in enumerate(opciones, 1):
        print(f"  {i}. {op}")
    while True:
        try:
            idx = int(input("Elige una opción (número): ").strip())
            if 1 <= idx <= len(opciones):
                return opciones[idx - 1]
        except ValueError:
            pass
        print("  Opción inválida, intenta de nuevo.")
 
 
def main():
    print("=" * 66)
    print(" SISTEMA EXPERTO — RECOMENDADOR DE CULTIVOS AGRÍCOLAS (COLOMBIA)")
    print("=" * 66)
    print()
 
    region = input("Región o departamento donde cultivarás: ").strip()
    msnm = pedir_float("Altitud del terreno (msnm): ")
    ph = pedir_float("pH del suelo (ej. 5.8): ")
    clima = pedir_opcion("Clima predominante en la zona:", ["Frío", "Templado", "Cálido"])
    presupuesto = pedir_float("Presupuesto disponible por hectárea (millones de COP): ")
    terreno = input("Tipo de terreno (opcional, ej. ladera, plano, ondulado): ").strip()
 
    hechos = HechosUsuario(
        region=region, msnm=msnm, ph=ph, clima=clima,
        presupuesto_millones=presupuesto, terreno=terreno,
    )
 
    motor = MotorInferencia(BASE_CONOCIMIENTO, PESOS)
    ranking = motor.inferir(hechos)
    mejor = ranking[0]
 
    print("\n" + "=" * 66)
    print(f" RECOMENDACIÓN PRINCIPAL: {mejor['cultivo']} "
          f"({mejor['compatibilidad']}% de compatibilidad)")
    print("=" * 66)
    print(f"\nPor qué encaja: {motor.explicar(mejor)}")
    print(f"\nInversión estimada: {mejor['presupuesto_sugerido']}")
    print(f"Primera cosecha: {mejor['primera_cosecha_anios']} años")
    print(f"\nRentabilidad:\n  {mejor['rentabilidad']}")
    print(f"\nCuidados y exigencias:\n  {mejor['cuidados']}")
 
    print("\n" + "-" * 66)
    print(" OTRAS OPCIONES COMPATIBLES (top 3 siguientes)")
    print("-" * 66)
    for i, r in enumerate(ranking[1:4], 2):
        print(f"\n{i}. {r['cultivo']} — {r['compatibilidad']}% de compatibilidad")
        print(f"   {motor.explicar(r)}")
 
    # Exporta el resultado completo a JSON por si se quiere integrar
    # con otra aplicación (web, app móvil, etc.)
    with open("resultado_recomendacion.json", "w", encoding="utf-8") as f:
        json.dump(
            {"hechos": hechos.__dict__, "ranking": ranking},
            f, ensure_ascii=False, indent=2,
        )
    print("\n(Resultado completo también guardado en resultado_recomendacion.json)")
 
 
if __name__ == "__main__":
    main()