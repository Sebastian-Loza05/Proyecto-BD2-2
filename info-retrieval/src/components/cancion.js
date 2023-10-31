"use client"
import styles from "@/styles/cancion.module.css" 
import React, { useState } from "react";
import Modal from 'react-modal'

Modal.setAppElement('#__next');

export default function Cancion({indice, cancion}) {
  const [modalOpen, setModalOpen] = useState(false);
  const handleClick = () => {
    setModalOpen(true);
  }

  const closeModal = () => {
    setModalOpen(false);
  }

  return (
    <div className={styles.cancion} >
      <section className={styles.item}>
        <p onClick={handleClick}> {indice+1}.- {cancion.nombre} - {cancion.artista} </p>
      </section>
      <section>
        <Modal
          isOpen={modalOpen}
          onRequestClose={closeModal}
          className={styles.customModal}
        >
          <div className={styles.modal}>
            <h3> {cancion.nombre} </h3>
            <p> {cancion.letra} </p>
            <button onClick={closeModal}> Cerrar </button>
          </div>
        </Modal>
      </section>
    </div>
  )
}
