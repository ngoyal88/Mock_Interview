import React, { useEffect, useRef } from "react";

const CandidateWebcam = () => {
  const videoRef = useRef(null);

  useEffect(() => {
    const currentVideo = videoRef.current;

    navigator.mediaDevices
      .getUserMedia({ video: true, audio: false })
      .then((stream) => {
        if (currentVideo) {
          currentVideo.srcObject = stream;
        }
      })
      .catch((err) => {
        console.error("Webcam error:", err);
      });

    return () => {
      if (currentVideo && currentVideo.srcObject) {
        currentVideo.srcObject.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  return (
    <video
      ref={videoRef}
      autoPlay
      muted
      playsInline
      className="w-full h-full object-cover transform scale-x-[-1]"
      disablePictureInPicture
      controls={false}
      onContextMenu={(e) => e.preventDefault()}
    />
  );
};

export default CandidateWebcam;
