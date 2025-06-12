import aiHero from "../assets/interview.svg";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white text-gray-800">

      <main className="flex flex-col-reverse lg:flex-row items-center justify-between max-w-7xl mx-auto px-4 py-16">
        <div className="lg:w-1/2">
          <h2 className="text-4xl font-extrabold mb-6 leading-tight">
            AI-Powered <span className="text-blue-600">Mock Interviews</span><br />
            for Aspiring Developers
          </h2>
          <p className="mb-6 text-lg text-gray-700">
            Simulate real-time technical and behavioral interviews powered by AI.
            Experience a dynamic, voice-based interviewer and get instant feedback.
          </p>

          <Link to="/start">
            <button className="bg-blue-600 text-white px-6 py-3 rounded-xl shadow hover:bg-blue-700 transition">
              Start Interview
            </button>
          </Link>
        </div>

        <div className="lg:w-1/2 mb-10 lg:mb-0">
          <img src={aiHero} alt="AI Interview Illustration" className="w-full max-w-md mx-auto" />
        </div>
      </main>
    </div>
  );
};

export default Home;

