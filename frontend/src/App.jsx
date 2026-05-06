import { useState } from "react";
import { API } from "./api";

export default function App() {

  const [files, setFiles] = useState([]);
  const [ratio, setRatio] = useState("standard");
  const [loading, setLoading] = useState(false);

  const upload = async () => {

    try {

      setLoading(true);

      const form = new FormData();

      files.forEach((file) => {
        form.append("files", file);
      });

      form.append(
        "ratio_type",
        ratio
      );

      const res = await API.post(
        "/crop",
        form,
        {
          responseType: "blob"
        }
      );

      const url =
        window.URL.createObjectURL(
          res.data
        );

      const a =
        document.createElement("a");

      a.href = url;

      a.download =
        "passport_photos.zip";

      a.click();

    } catch (err) {

      console.error(err);

      alert(
        "Server error."
      );

    } finally {

      setLoading(false);

    }
  };

  return (

    <div className="container">

      <h1>
        Passport Photo Cropper
      </h1>

      <select
        value={ratio}
        onChange={(e) =>
          setRatio(
            e.target.value
          )
        }
      >

        <option value="standard">
          Standard
        </option>

        <option value="square">
          Square
        </option>

      </select>

      <input
        type="file"
        multiple
        accept="image/*"
        onChange={(e) =>
          setFiles(
            [...e.target.files]
          )
        }
      />

      <button
        onClick={upload}
        disabled={
          loading ||
          files.length === 0
        }
      >

        {
          loading
            ? "Processing..."
            : "Crop Photos"
        }

      </button>

    </div>
  );
}
