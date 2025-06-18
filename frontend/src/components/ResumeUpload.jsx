import React, { useState } from 'react';

const ResumeUpload = ({ onParsed }) => {
  const [file, setFile] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      setError('');
      const res = await fetch('http://localhost:8000/upload_resume', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error('Upload failed');
      }

      const data = await res.json();
      setParsedData(data.parsed_data);
      onParsed && onParsed(data.parsed_data);
    } catch (err) {
      setError('Failed to upload or parse resume');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 shadow-md rounded-lg mt-6">
      <h2 className="text-xl font-bold mb-4">Upload Your Resume</h2>

      <input type="file" accept=".pdf" onChange={handleFileChange} className="mb-4" />
      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        {loading ? 'Uploading...' : 'Upload'}
      </button>

      {error && <p className="text-red-500 mt-2">{error}</p>}

      {parsedData && (
        <div className="mt-6 bg-gray-100 p-4 rounded">
          <h3 className="text-lg font-semibold">Parsed Resume Data:</h3>
          <pre className="text-sm mt-2">{JSON.stringify(parsedData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;
