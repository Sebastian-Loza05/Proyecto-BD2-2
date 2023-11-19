"use client"
import styles from './page.module.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import { useState } from 'react';
import Results from '@/components/results';
import { getTopKByInvert, getTopKByPostgres } from './api';

export default function Home() {
  const [formData, setFormData] = useState({
    textQuery: '',
    topK: 0,
  });
  const [tipo, setTipo] = useState(null);

  const [results, setResults] = useState([]);

  const handleInputChange = (e) => {
    const {name, value} = e.target;
    setFormData({
      ...formData,
      [name]:value
    });
  }

  const handleTipoChange = (e) => {
    const value = e.target.value;
    setTipo(value);
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    let data;
    console.log("oe");
    if (tipo == "postgres"){
      data = await getTopKByPostgres(formData);
    } else {
      data = await getTopKByInvert(formData);
    }
    console.log("data: ", data);
    setResults(data);
  }

  return (
    <main className={styles.main}>
      <h1 className={styles.h1}> Information Retrieval </h1>
      <h1 className={styles.h1}>  
        BD2 
        <span>
          <i className="bi bi-database-fill"></i>
        </span>
      </h1>
      <div className={styles.body}>
        <section className={styles.formulario}>
          <form onSubmit={handleSubmit}>
            <label> Ingresa tu consulta textual 
              <strong className={styles.arrow}>
                <i className="bi bi-arrow-right"></i>
              </strong>
              <input 
                type="text" 
                name="textQuery"
                value={formData.textQuery}
                onChange={handleInputChange}
                placeholder="Ingresa la consulta textual"
              />
            </label>
            <label> Ingrese el topK a recuperar 
              <strong className={styles.arrow}>
                <i className="bi bi-arrow-right"></i>
              </strong>
              <input 
                type="number"
                name="topK"
                value={formData.topK}
                onChange={handleInputChange}
                placeholder="Ingresa la consulta textual"
              />
            </label>
            <label> Escoge el índice que usarás 
              <strong className={styles.arrow}>
                <i className="bi bi-arrow-right"></i>
              </strong>
              <select name="tipo" value={tipo} onChange={handleTipoChange}>
                <option value=""> Seleccciona una opción </option>
                <option value="postgres">Postgres SQL </option>
                <option value="invert">Índice propio </option>
              </select>
            </label>
            <button type="submit"> Enviar </button>
          </form>
        </section>
        <section className={styles.results}>
          { 
            (results.length === 0) ? 
            <h2> No hay datos aun</h2> :(
              <Results results={results}/>
            )
          }
        </section>
      </div>
    </main>
  )
}
