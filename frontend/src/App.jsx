import { useState } from "react";
import { API } from "./api";

export default function App() {

  const [files, setFiles] =
    useState([]);

  const [ratio, setRatio] =
    useState("standard");

  const [loading, setLoading] =
    useState(false);

  const [progress, setProgress] =
    useState("");

  const [doneCount, setDoneCount] =
    useState(0);



  const upload = async () => {

    let timer;


    try {

      setLoading(true);

      setDoneCount(0);

      setProgress(
        "Starting..."
      );


      // Create job first
      const jobForm =
        new FormData();

      jobForm.append(
        "total",
        files.length
      );

      const jobRes =
        await API.post(
          "/create-job",
          jobForm
        );


      const jobId =
        jobRes.data.job_id;


      // Start polling immediately
      timer =
        setInterval(

          async () => {

            const p =
              await API.get(
                `/progress/${jobId}`
              );


            setDoneCount(
              p.data.done || 0
            );


            setProgress(
              `${p.data.done}/${p.data.total}
               → ${p.data.current}`
            );


            if (
              p.data.finished
            ) {

              clearInterval(
                timer
              );


              setProgress(
                "Completed ✓"
              );

            }

          },

          1000

        );



      const form =
        new FormData();


      files.forEach(
        file => {

          form.append(
            "files",
            file
          );

        }
      );


      form.append(
        "ratio_type",
        ratio
      );


      form.append(
        "job_id",
        jobId
      );



      const res =
        await API.post(

          "/crop",

          form,

          {
            responseType:
              "blob"
          }

        );



      const url =
        window.URL.createObjectURL(

          new Blob(
            [res.data]
          )

        );



      const a =
        document.createElement(
          "a"
        );


      a.href = url;

      a.download =
        "passport_photos.zip";

      a.click();

    }


    catch (error) {

      console.error(
        error
      );


      if (timer) {

        clearInterval(
          timer
        );

      }


      setProgress(
        "Something went wrong"
      );

    }


    finally {

      setLoading(
        false
      );

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



      <div className="progress-box">

        <div className="progress-text">

          {progress}

        </div>



        {

          loading && (

            <div className="progress-bar">

              <div

                className="progress-fill"

                style={{

                  width:
                    `${(
                      doneCount /
                      files.length
                    ) * 100}%`

                }}

              />

            </div>

          )

        }

      </div>

    </div>

  );

}