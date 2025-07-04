import questions from "../data/questions.json";

export const getRandomDSAQuestion = (level = "easy") => {
  const filtered = questions.filter((q) => q.difficulty === level);
  return filtered[Math.floor(Math.random() * filtered.length)];
};
