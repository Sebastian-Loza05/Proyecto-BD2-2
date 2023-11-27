"use client"
import React, { useState } from 'react';
import styles from './spoti.module.css'; // Asegúrate de que las clases de estilo se importan correctamente
import axios from 'axios';

function Spoti() {
  const [activeItem, setActiveItem] = useState('Home');
  const [algorithm, setAlgorithm] = useState('KNN');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [selectedSong, setSelectedSong] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [searchMethod, setSearchMethod] = useState('My Index');
  const [searchNumber, setSearchNumber] = useState(10);
  const [selectedFile, setSelectedFile] = useState(null);
  const [songs, setSongs] = useState([
    { track_name: 'Un Peso', track_artist: 'J Balvin', duration: '3:30', imageUrl:'https://cdn.discordapp.com/attachments/1155323431915630594/1178543286206611539/ab67616d0000b2734891d9b25d8919448388f3bb.jpeg?ex=657686f7&is=656411f7&hm=8ced1986172409120b4f7ca402a579c6afdc65958d59292617dd9562336797a7&', lyrics: 'Hola'},
    { track_name: 'Un Preview', track_artist: 'Bad Bunny', duration: '2:00', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178546977194123305/Bad_Bunny_-_Un_Preview.png?ex=65768a67&is=65641567&hm=ec952bf01e4595dd05e85d2c0dd2efe3f7b4782b1a59032575f9cbd0f424503d&', lyrics: 'Hola'},
    { track_name: 'LALA', track_artist: 'Mike Towers', duration: '2:50', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547097679704094/Sin-titulo-1.jpg?ex=65768a84&is=65641584&hm=1cbd619e375ca982fee7bff85b34b9b562388860d0d9bff6422832f77ae3bb09&', lyrics: 'Hola'},
    { track_name: 'Lo que hay x aqui', track_artist: 'Rels B', duration: '3:00', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547323811418113/ab67616d0000b27385acf6becb994eb3cf3edd15.jpeg?ex=65768aba&is=656415ba&hm=59d20b6b443696f96d67fbe2653310f0c36be540ce001fd1080b4e7474636c5c&', lyrics: 'Hola'},
    { track_name: 'Columbia', track_artist: 'Quevedo', duration: '6:70', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547337832964178/ab67616d0000b273a00a817b017c6f6bf8460be9.jpeg?ex=65768abd&is=656415bd&hm=712a85140e20724f07a80b4401795dfdc1de7873913d884673a1a8e358fbe4df&' , lyrics: 'Hola'},
    { track_name: 'Vagabundo', track_artist: 'Sebastian Yatra', duration: '4:10', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547353142169611/ab67616d0000b2732d6016751b8ea5e66e83cd04.jpeg?ex=65768ac1&is=656415c1&hm=5a25cf9b4aa00a95abdd00467c89f4cc9c8283508c98d3f898e40db5c36ac468&', lyrics: 'Hola'},
    { track_name: 'Un Finde', track_artist: 'Big One', duration: '3:50', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547424172703835/ab67616d0000b273fc9ce77ab8fcd9eadda3acd3.jpeg?ex=65768ad2&is=656415d2&hm=1e535422aef99230a01e06303db1d45e2e9fb3c3fc8a2927be87110df517811d&', lyrics: 'Hola'},
    { track_name: 'La Diferencia', track_artist: 'Wampy', duration: '3:36', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178668402563362826/maxresdefault_1.jpg?ex=6576fb7d&is=6564867d&hm=cd23955d96ebd764aa650612f7654e31aa6524802179c50d37dd532102b2bf9b&', lyrics: 'Hola'},
    { track_name: 'Ojitos Lindos', track_artist: 'Bad Bunny', duration: '3:30', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178668553579286538/descarga_3.jpeg?ex=6576fba1&is=656486a1&hm=8d2003425bc0f453308af7f33023d65dc1ec969c3136457ca16b5318b3c728b1&', lyrics: 'Hola'},
    { track_name: 'One Day', track_artist: 'Tainy', duration: '3:30', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547609011494983/J_Balvin_-_Un_Dia_One_Day.png?ex=65768afe&is=656415fe&hm=06b16133e70ffda3da54e400499fac4a91cd201314b35d53d345f92ac28ca8b5&', lyrics: 'Hola'},
  ]);

  const handleHomeClick = () => {
    setActiveItem('Home');
    // Restablece las canciones a su estado inicial
    setSongs([
      { track_name: 'Un Peso', track_artist: 'J Balvin', duration: '3:30', imageUrl:'https://cdn.discordapp.com/attachments/1155323431915630594/1178543286206611539/ab67616d0000b2734891d9b25d8919448388f3bb.jpeg?ex=657686f7&is=656411f7&hm=8ced1986172409120b4f7ca402a579c6afdc65958d59292617dd9562336797a7&', lyrics: 'Hola'},
      { track_name: 'Un Preview', track_artist: 'Bad Bunny', duration: '2:00', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178546977194123305/Bad_Bunny_-_Un_Preview.png?ex=65768a67&is=65641567&hm=ec952bf01e4595dd05e85d2c0dd2efe3f7b4782b1a59032575f9cbd0f424503d&', lyrics: 'Hola'},
      { track_name: 'LALA', track_artist: 'Mike Towers', duration: '2:50', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547097679704094/Sin-titulo-1.jpg?ex=65768a84&is=65641584&hm=1cbd619e375ca982fee7bff85b34b9b562388860d0d9bff6422832f77ae3bb09&', lyrics: 'Hola'},
      { track_name: 'Lo que hay x aqui', track_artist: 'Rels B', duration: '3:00', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547323811418113/ab67616d0000b27385acf6becb994eb3cf3edd15.jpeg?ex=65768aba&is=656415ba&hm=59d20b6b443696f96d67fbe2653310f0c36be540ce001fd1080b4e7474636c5c&', lyrics: 'Hola'},
      { track_name: 'Columbia', track_artist: 'Quevedo', duration: '6:70', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547337832964178/ab67616d0000b273a00a817b017c6f6bf8460be9.jpeg?ex=65768abd&is=656415bd&hm=712a85140e20724f07a80b4401795dfdc1de7873913d884673a1a8e358fbe4df&' , lyrics: 'Hola'},
      { track_name: 'Vagabundo', track_artist: 'Sebastian Yatra', duration: '4:10', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547353142169611/ab67616d0000b2732d6016751b8ea5e66e83cd04.jpeg?ex=65768ac1&is=656415c1&hm=5a25cf9b4aa00a95abdd00467c89f4cc9c8283508c98d3f898e40db5c36ac468&', lyrics: 'Hola'},
      { track_name: 'Un Finde', track_artist: 'Big One', duration: '3:50', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547424172703835/ab67616d0000b273fc9ce77ab8fcd9eadda3acd3.jpeg?ex=65768ad2&is=656415d2&hm=1e535422aef99230a01e06303db1d45e2e9fb3c3fc8a2927be87110df517811d&', lyrics: 'Hola'},
      { track_name: 'La Diferencia', track_artist: 'Wampy', duration: '3:36', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178668402563362826/maxresdefault_1.jpg?ex=6576fb7d&is=6564867d&hm=cd23955d96ebd764aa650612f7654e31aa6524802179c50d37dd532102b2bf9b&', lyrics: 'Hola'},
      { track_name: 'Ojitos Lindos', track_artist: 'Bad Bunny', duration: '3:30', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178668553579286538/descarga_3.jpeg?ex=6576fba1&is=656486a1&hm=8d2003425bc0f453308af7f33023d65dc1ec969c3136457ca16b5318b3c728b1&', lyrics: 'Hola'},
      { track_name: 'One Day', track_artist: 'Tainy', duration: '3:30', imageUrl:'https://cdn.discordapp.com/attachments/1166998304937222166/1178547609011494983/J_Balvin_-_Un_Dia_One_Day.png?ex=65768afe&is=656415fe&hm=06b16133e70ffda3da54e400499fac4a91cd201314b35d53d345f92ac28ca8b5&', lyrics: 'Hola'},
    ]);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      console.log(file);
      setUploadProgress(0);
      setIsUploading(true);
      setFileUploaded(false);
  
      // Simula la carga del archivo
      const interval = setInterval(() => {
        setUploadProgress((oldProgress) => {
          const newProgress = Math.min(oldProgress + 10, 100);
          if (newProgress === 100) {
            clearInterval(interval);
            setIsUploading(false);
            setFileUploaded(true); // Indica que el archivo se ha cargado
          }
          return newProgress;
        });
      }, 500);
    }
  };

  const defaultRightContent = (
    <div className={styles.defaultRight}>
      <img src="https://cdn.discordapp.com/attachments/1155323431915630594/1178600841394016317/6532493.png?ex=6576bc91&is=65644791&hm=d5d99fef558ed5539b9ed9f59b1358d0d5a67fdd3d5a3c193c2b04247632f3dd&" alt="Bienvenido" className={styles.defaultImage} />
      <div className={styles.welcomeMessage}>
        Bienvenido a Pineapple Music! Elige una canción para visualizar su letra. No te acuerdas el nombre 
        de la canción? No hay problema, también contamos con un buscador por audio muy útil para usted 😉👌.
      </div>
    </div>
  );

  const menuItems = [
    { name: 'Home', icon: '🏠' },
    { name: 'Buscar', icon: '🔍' },
    { name: 'Your Library', icon: '📚' }
  ];

  const playlists = [
    { name: 'Top 100 Peru', creator: 'Playlist by Luis Golac' },
    { name: 'Daily Mix', creator: 'Playlist by Sebastian Loza' },
    { name: 'Viva Latino', creator: 'Playlist by Aaron Coorahua' },
    { name: 'Hits Urbanos', creator: 'Playlist by Cesar Pajuelo' },
    { name: 'Musica Sad', creator: 'Playlist by Gonzalo Rodriguez' }
  ];

  const handleSongClick = (song) => {
    setSelectedSong(song);
  };

  const handleSearchChange = (e) => {
    setSearchText(e.target.value);
  };

  const handleNumberChange = (e) => {
    setSearchNumber(e.target.value);
  };

  const handleMethodChange = (e) => {
    setSearchMethod(e.target.value);
  };

  const searchSongs = async () => {
    setActiveItem('Buscar');
    try {
      console.log(searchMethod);
      let endpoint = '';
      if (searchMethod === 'PostgreSQL') {
        endpoint = 'http://127.0.0.1:5000/psql';
      } else if (searchMethod === 'MyIndex') {
        endpoint = 'http://127.0.0.1:5000/invert_index';
      }
      const response = await axios.post(endpoint, {
        textQuery: searchText,
        topK: searchNumber
      });

      if (response.status === 200) {
        const searchResults = response.data.map((song) => ({
          ...song,
          duration: convertMsToMinutesSeconds(song.duration_ms),
          imageUrl: 'https://cdn.discordapp.com/attachments/1166998304937222166/1178547424172703835/ab67616d0000b273fc9ce77ab8fcd9eadda3acd3.jpeg?ex=65768ad2&is=656415d2&hm=1e535422aef99230a01e06303db1d45e2e9fb3c3fc8a2927be87110df517811d&'
        }));
        setSongs(searchResults);
      } else {
        console.error('Error en la búsqueda:', response.status);
      }
    } catch (error) {
      console.error('Error en la conexión:', error);
    }
  };

  const convertMsToMinutesSeconds = (ms) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = ((ms % 60000) / 1000).toFixed(0);
    return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
  };

  const handleScanClick = async () => {
    setActiveItem('Your Library');
    const formData = new FormData();
    console.log('Botón escanear presionado');
    formData.append('audio', selectedFile);
    formData.append('json', JSON.stringify({ topK: searchNumber }));
    let endpoint = '';
    switch (algorithm) {
      case 'KNN':
        endpoint = '/knn'; // Asegúrate de que la ruta esté en minúsculas si así está definida en el backend
        break;
      case 'FAISS':
        endpoint = '/faiss';
        break;
      case 'RTREE':
        endpoint = '/rtree';
        break;
      default:
        console.error('Algoritmo no reconocido');
        return;
    }
    try {
      const response = await axios.post(`http://127.0.0.1:5000${endpoint}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
  
      if (response.status === 200) {
        const searchResults = response.data.map((song) => ({
          ...song,
          duration: convertMsToMinutesSeconds(song.duration_ms),
        }));
        setSongs(searchResults);
      } else {
        console.error('Error en la búsqueda:', response.status);
      }
    } catch (error) {
      console.error('Error en la conexión:', error);
    }
  };

  const defaultPlaylistImageUrl = "https://cdn.discordapp.com/attachments/1155323431915630594/1178542876972556379/rock-music-icon-vinyl-record-png.webp?ex=65768696&is=65641196&hm=06e5d54224876a15d3a766ad6695cfb570c0427db4850f9c46235034bf599d92&";
  
  return(
    <main className={styles.container}>
      <div className={styles.header}> 
        <h1>Pineapple Music</h1>
        <img src="https://cdn.discordapp.com/attachments/1155323431915630594/1178600841394016317/6532493.png?ex=6576bc91&is=65644791&hm=d5d99fef558ed5539b9ed9f59b1358d0d5a67fdd3d5a3c193c2b04247632f3dd&" alt="Bienvenido" className={styles.logo} />
      </div>
      <div className={styles.content}>
        <div className={styles.columns}>
          <div className={`${styles.columnLeft} ${styles.columnScroll}`}>
              {menuItems.map(item => (
              <div key={item.name} 
                  className={`${styles.item} ${activeItem === item.name ? styles.activeItem : ''}`} 
                  onClick={() => item.name === 'Home' ? handleHomeClick() : setActiveItem(item.name)}>
                <span className={styles.icon}>{item.icon}</span>
                <span className={styles.text}>{item.name}</span>
              </div>
            ))}
            <div className={styles.playlists}>
                {playlists.map((playlist, index) => (
                  <div key={index} className={styles.playlistItem}>
                    <img src={defaultPlaylistImageUrl} alt={playlist.name} className={styles.playlistImage} />
                    <div>
                      <div className={styles.playlistName}>{playlist.name}</div>
                      <div className={styles.playlistCreator}>{playlist.creator}</div>
                    </div>
                  </div>
                ))}
            </div>
          
            <div className={styles.fileContainer}>
              <input
                type="file"
                onChange={handleFileUpload}
                className={styles.hiddenFileInput}
                // Agrega la clave "key" para reiniciar el componente input después de una carga
                key={uploadProgress}
              />
              <button className={styles.uploadButton}>Upload</button>
              {isUploading && (
                <div className={styles.progressBarContainer}>
                  <div className={styles.progressBar} style={{ width: `${uploadProgress}%` }}></div>
                </div>
              )}
              
            </div>
            <button className={styles.scanButton} onClick={handleScanClick}>Escanear</button>
            <select
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              className={`${styles.selectField} ${styles.selectInput}`}
            >
              <option value="KNN">KNN</option>
              <option value="FAISS">FAISS</option>
              <option value="RTREE">RTREE</option>
            </select>
          </div>
          <div className={`${styles.columnMiddle} ${styles.columnScroll}`}>
          <div className={styles.searchContainer}>
              <input
                type="text"
                placeholder="Search"
                value={searchText}
                onChange={handleSearchChange}
                className={`${styles.inputField} ${styles.searchBar}`} 
              />
              
              <input
                type="number"
                placeholder="Top K"
                value={searchNumber} 
                onChange={handleNumberChange} 
                className={styles.inputField}
              />
              
              <select 
                className={`${styles.selectField} ${styles.selectInput}`}
                value={searchMethod}
                onChange={handleMethodChange}
              >
                <option value="MyIndex">My Index</option>
                <option value="PostgreSQL">PostgreSQL</option>
              </select>
              <button onClick={searchSongs} className={styles.searchButton}>Buscar</button>
            </div>
            
            <div className={styles.songsContainer}>
              {songs.map((song, index) => (
                <div key={index} className={styles.songCard} onClick={() => handleSongClick(song)}>
                  <img src={song.imageUrl} alt={song.title} className={styles.songImage} />
                  <div className={styles.songDetails}>
                    <div className={styles.songTitle}>{song.track_name}</div>
                    <div className={styles.songArtist}>{song.track_artist}</div>
                    <div className={styles.songDuration}>{song.duration}</div>   
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className={`${styles.columnRight} ${styles.columnScroll}`}>
            {selectedSong ? (
              <div className={styles.songContent}>
                <img src={selectedSong.imageUrl} alt={selectedSong.title} className={styles.songImage} />
                <div className={styles.songDetails}>
                  <div className={styles.songTitle}>{selectedSong.track_name}</div>
                  <div className={styles.songArtist}>{selectedSong.track_artist}</div>
                  <div className={styles.songDuration}>{selectedSong.duration}</div>
                </div>
                <div className={styles.songLyrics}>
                  {selectedSong.lyrics}
                </div>
              </div>
            ) : (
              defaultRightContent
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

export default Spoti;