"use client"
import styles from './page.module.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import { useState } from 'react';
import Results from '@/components/results';

export default function Home() {
  const [formData, setFormData] = useState({
    textQuery: '',
    topK: 0,
    tipo: ''
  });

  const [results, setResults] = useState([
    {
      nombre: "Cancion 1",
      artista: "Diana",
      letra: "Diana es muy gei le gusta comer puré de papa y tallarines a lo alfredo lalalalalalalalalalaalalalalalalalalalalalalala"
    },
    {
      nombre: "Cancion 2",
      artista: "Sebastián",
      letra: "Sebastian es un tipo random lolololololol le gustan los carros y Diana sobre todo."
    }
  ]);

  const handleInputChange = (e) => {
    const {name, value} = e.target;
    setFormData({
      ...formData,
      [name]:value
    });
  }

  const handleSubmit = (e) => {
    e.preventDefault();
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
              <select name="tipo" value={formData.tipo} onChange={handleInputChange}>
                <option value=""> Seleccciona una opción </option>
                <option value="postgres">Postgres SQL </option>
                <option value="Propio">Índice propio </option>
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
