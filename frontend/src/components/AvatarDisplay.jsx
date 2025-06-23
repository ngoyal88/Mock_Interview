import React from "react";

const AvatarDisplay = ({ videoUrl, loading }) => {
  return (
    <div className="w-full aspect-video bg-gray-200 flex items-center justify-center rounded shadow-inner">
      {loading ? (
        <p className="text-gray-500 text-center">Generating avatar...</p>
      ) : videoUrl ? (
        <video key={videoUrl} src={videoUrl} autoPlay controls className="rounded w-full" />
      ) : (
        <p className="text-red-500 text-center">Failed to load avatar.</p>
      )}
    </div>
  );
};

export default AvatarDisplay;
