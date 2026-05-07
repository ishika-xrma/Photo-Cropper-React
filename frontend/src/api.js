import axios from "axios";


export const API =
  axios.create({

    baseURL:
      "https://photo-cropper-react.onrender.com",

    timeout: 0

  });