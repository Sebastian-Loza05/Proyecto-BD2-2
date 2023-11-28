import styles from "@/styles/cancion.module.css" 
import React, { useState, useEffect } from "react";
import Modal from 'react-modal'

export default function Cancion({indice, cancion}) {
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    Modal.setAppElement('#__next');
  }, []);
  const handleClick = () => {
    setModalOpen(true);
  }

  const closeModal = () => {
    setModalOpen(false);
  }

  return (
    <div className={styles.cancion} >
      <section className={styles.item} onClick={handleClick}>
        <p > {indice+1}.- {cancion.track_name} - {cancion.track_artist} </p>
      </section>
      <section>
        <Modal
          isOpen={modalOpen}
          onRequestClose={closeModal}
          className={styles.customModal}
        >
          <div className={styles.modal}>
            <h3> {cancion.track_name} </h3>
            <p> {cancion.lyrics} </p>
            <button onClick={closeModal}> Cerrar </button>
          </div>
        </Modal>
      </section>
    </div>
  )
}
