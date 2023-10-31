"use client"
import React from "react";
import Cancion from "./cancion";
import styles from "@/styles/Results.module.css"

export default function Results({results}) {
  
  const canciones = [];
  for (let i = 0; i < results.length; i++) {
    canciones.push(<Cancion key={i} indice={i} cancion={results[i]} />);
  }
  return (
    <div className={styles.results}>
      <h3> Top K </h3>
      {canciones}
    </div>
  )
};
