import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api";

function App() {
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
    } catch (err) {
      console.error(err);
      setError("Ocurrió un error al evaluar el riesgo.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto", padding: "2rem", fontFamily: "system-ui, sans-serif" }}>
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
                <strong>{pregunta.id}. {pregunta.texto}</strong>
              </p>

              {/* bool y select usan opciones */}
              {(pregunta.tipo === "bool" || pregunta.tipo === "select") && (
                <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
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

              {/* Por si en el futuro usamos preguntas numéricas */}
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

          {resultado.explicabilidad && resultado.explicabilidad.reglas_activadas && (
            <>
              <h3>Reglas activadas</h3>
              <ul>
                {resultado.explicabilidad.reglas_activadas.map((r) => (
                  <li key={r.regla_id}>
                    <strong>{r.nombre}</strong> — Diagnóstico: {r.diagnostico} (peso {r.peso})
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
