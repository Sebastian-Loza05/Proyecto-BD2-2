"use client"
import styles from './page.module.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import { useState } from 'react';

export default function Home() {
  const [inputValue, setInputValue] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
  }

  return (
    <main className={styles.main}>
      <h1 className={styles.h1}> Iformation Retrieval </h1>
      <h1 className={styles.h1}>  
        BD2 
        <span>
          <i class="bi bi-database-fill"></i>
        </span>
      </h1>
      <div className={styles.body}>
        <section>
          <form onSubmit={handleSubmit}>
            <label> Ingresa tu consulta textual 
              <strong className={styles.arrow}>
                <i class="bi bi-arrow-right"></i>
              </strong>
            </label>
            <input 
              type="text" 
              value={inputValue}
              placeholder="Ingresa la consulta textual"
            />
          </form>
        </section>
      </div>
    </main>
  )
}
