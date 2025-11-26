import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api";

function App() {
  const [rutaMejora, setRutaMejora] = useState(null);
  const [cargandoIA, setCargandoIA] = useState(false);
  const [preguntas, setPreguntas] = useState([]);
  const [respuestas, setRespuestas] = useState({});
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [resultado, setResultado] = useState(null);

  // Cargar preguntas desde el backend
  useEffect(() => {
    const fetchPreguntas = async () => {
      try {
        setCargando(true);
        const resp = await fetch(`${API_BASE_URL}/preguntas/`);
        if (!resp.ok) {
          throw new Error("Error al obtener las preguntas");
        }
        const data = await resp.json();
        setPreguntas(data);

        // Inicializar respuestas con valores vacíos
        const inicial = {};
        data.forEach((p) => {
          inicial[p.id] = "";
        });
        setRespuestas(inicial);
      } catch (err) {
        console.error(err);
        setError("No se pudieron cargar las preguntas.");
      } finally {
        setCargando(false);
      }
    };

    fetchPreguntas();
  }, []);

  const handleChange = (preguntaId, valor) => {
    setRespuestas((prev) => ({
      ...prev,
      [preguntaId]: valor,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResultado(null);

    // Validar que todas las preguntas tengan respuesta
    const faltantes = preguntas.filter((p) => !respuestas[p.id]);
    if (faltantes.length > 0) {
      setError("Por favor responde todas las preguntas antes de evaluar.");
      return;
    }

    const payload = {
      respuestas: Object.entries(respuestas).map(([preguntaId, valor]) => ({
        preguntaId: Number(preguntaId),
        valor,
      })),
    };

    try {
      setCargando(true);
      const resp = await fetch(`${API_BASE_URL}/evaluar/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const dataError = await resp.json().catch(() => ({}));
        console.error("Error en evaluación:", dataError);
        throw new Error("Error al evaluar el riesgo.");
      }

      const data = await resp.json();
      setResultado(data);
      setRutaMejora(null);
    } catch (err) {
      console.error(err);
      setError("Ocurrió un error al evaluar el riesgo.");
    } finally {
      setCargando(false);
    }
  };

  const handleRutaMejora = async () => {
    if (!resultado) return;

    setCargandoIA(true);
    setRutaMejora(null);
    setError(null);

    const payload = {
      riesgo: resultado.riesgo,
      puntaje: resultado.puntaje,
      recomendaciones: resultado.recomendaciones,
      reglas_activadas: resultado.explicabilidad?.reglas_activadas || [],
    };

    try {
      const resp = await fetch(`${API_BASE_URL}/ruta-mejora/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const dataError = await resp.json().catch(() => ({}));
        console.error("Error en ruta-mejora:", dataError);
        throw new Error("Error al generar la ruta de mejora.");
      }

      const data = await resp.json();
      setRutaMejora(data.ruta_mejora);
    } catch (err) {
      console.error(err);
      setError("Ocurrió un error al pedir la ruta de mejora a la IA.");
    } finally {
      setCargandoIA(false);
    }
  };


return (
  <div
    style={{
      maxWidth: "900px",
      margin: "0 auto",
      padding: "2rem",
      fontFamily: "system-ui, sans-serif",
    }}
  >
    <h1>Sistema Experto: Evaluador de Riesgos de TI</h1>
    <p>
      Responde el siguiente cuestionario para obtener una evaluación básica
      del nivel de riesgo de TI de la organización.
    </p>

    {cargando && <p>Cargando...</p>}
    {error && <p style={{ color: "red" }}>{error}</p>}

    {!cargando && preguntas.length > 0 && (
      <form onSubmit={handleSubmit} style={{ marginTop: "1.5rem" }}>
        {preguntas.map((pregunta) => (
          <div
            key={pregunta.id}
            style={{
              marginBottom: "1.5rem",
              padding: "1rem",
              border: "1px solid #ddd",
              borderRadius: "8px",
            }}
          >
            <p style={{ marginBottom: "0.75rem" }}>
              <strong>
                {pregunta.id}. {pregunta.texto}
              </strong>
            </p>

            {(pregunta.tipo === "bool" || pregunta.tipo === "select") && (
              <div
                style={{
                  display: "flex",
                  gap: "1rem",
                  flexWrap: "wrap",
                }}
              >
                {pregunta.opciones.map((opcion) => (
                  <label key={opcion.id} style={{ cursor: "pointer" }}>
                    <input
                      type="radio"
                      name={`pregunta-${pregunta.id}`}
                      value={opcion.valor}
                      checked={respuestas[pregunta.id] === opcion.valor}
                      onChange={(e) =>
                        handleChange(pregunta.id, e.target.value)
                      }
                      style={{ marginRight: "0.5rem" }}
                    />
                    {opcion.etiqueta}
                  </label>
                ))}
              </div>
            )}

            {pregunta.tipo === "number" && (
              <input
                type="number"
                value={respuestas[pregunta.id] || ""}
                onChange={(e) =>
                  handleChange(pregunta.id, e.target.value)
                }
              />
            )}
          </div>
        ))}

        <button
          type="submit"
          disabled={cargando}
          style={{
            padding: "0.75rem 1.5rem",
            fontSize: "1rem",
            backgroundColor: "#2563eb",
            color: "white",
            border: "none",
            borderRadius: "999px",
            cursor: "pointer",
          }}
        >
          Evaluar riesgo
        </button>
      </form>
    )}

    {resultado && (
      <div
        style={{
          marginTop: "2rem",
          padding: "1.5rem",
          borderRadius: "8px",
          border: "1px solid #ddd",
          backgroundColor: "#f9fafb",
        }}
      >
        <h2>Resultado de la evaluación</h2>
        <p>
          <strong>Riesgo: </strong>
          <span
            style={{
              color:
                resultado.riesgo === "ALTO"
                  ? "red"
                  : resultado.riesgo === "MEDIO"
                  ? "#d97706"
                  : "green",
              fontWeight: "bold",
            }}
          >
            {resultado.riesgo}
          </span>
        </p>
        <p>
          <strong>Puntaje total:</strong> {resultado.puntaje}
        </p>

        <h3>Recomendaciones</h3>
        <ul>
          {resultado.recomendaciones.map((rec, idx) => (
            <li key={idx}>{rec}</li>
          ))}
        </ul>

        {resultado.explicabilidad &&
          resultado.explicabilidad.reglas_activadas && (
            <>
              <h3>Reglas activadas</h3>
              <ul>
                {resultado.explicabilidad.reglas_activadas.map((r) => (
                  <li key={r.regla_id}>
                    <strong>{r.nombre}</strong> — Diagnóstico:{" "}
                    {r.diagnostico} (peso {r.peso})
                  </li>
                ))}
              </ul>
            </>
          )}

        {/* Botón de IA + ruta de mejora dentro del mismo div */}
        <button
          type="button"
          onClick={handleRutaMejora}
          disabled={cargandoIA}
          style={{
            marginTop: "1rem",
            padding: "0.5rem 1rem",
            fontSize: "0.95rem",
            backgroundColor: "#0f766e",
            color: "white",
            border: "none",
            borderRadius: "999px",
            cursor: "pointer",
          }}
        >
          {cargandoIA
            ? "Generando ruta con IA..."
            : "Generar ruta de mejora con IA"}
        </button>

        {rutaMejora && (
          <div
            style={{
              marginTop: "1.5rem",
              padding: "1rem",
              borderRadius: "8px",
              border: "1px solid #ddd",
              backgroundColor: "#ecfeff",
              whiteSpace: "pre-wrap",
            }}
          >
            <h3>Ruta de mejora sugerida por IA</h3>
            <p>{rutaMejora}</p>
          </div>
        )}
      </div>
    )}
  </div>
);
}


export default App;
