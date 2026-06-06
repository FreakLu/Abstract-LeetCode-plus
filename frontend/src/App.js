import React, { useEffect } from "react";
import StudyWorkspace from "./components/StudyWorkspace";
import "./App.css";

function App() {
    useEffect(() => {
        document.title = "Abstract LeetCode Plus +"; // ✅ Set tab name
    }, []);
  return (
      <div className="App">
        <StudyWorkspace />
      </div>
  );
}

export default App;
