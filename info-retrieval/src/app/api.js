const URL = "http://127.0.0.1:5000/"

export const getTopKByInvert = async (form) => {
  try {
    const response = await fetch(URL + "/invert_index", {
      method: 'POST',
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(form)
    })
    return await response.json()

  } catch (error) {
    console.error(error);
  }
}

export const getTopKByPostgres = async (form) => {
  try {
    const response = await fetch(URL + "/psql", {
      method: 'POST',
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(form)
    })
    return await response.json()

  } catch (error) {
    console.error(error);
  }
}
