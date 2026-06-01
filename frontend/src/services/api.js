export const solveQuestion = async (question, language, onChunk) => {
    const API_URL = "http://127.0.0.1:8000/api/solve/";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question, language })
        });

        if (!response.ok) return { error: "HTTP error" };

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let fullText = "";

        // 真正的流式读取：只要有数据就读，读到一个字就通过 onChunk 传给组件
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            fullText += decoder.decode(value, { stream: true });
            if (onChunk) onChunk(fullText); // 实时抛出文字
        }
        
        return { response: fullText };
    } catch (error) {
        return { error: "Failed to connect to the server." };
    }
};

export const downloadExcel = async () => {
    const API_URL = "http://127.0.0.1:8000/api/download/";

    try {
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error("Failed to download file");
        }

        // Create a blob object from the response
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        // Create a temporary link and trigger the download
        const a = document.createElement("a");
        a.href = url;
        a.download = "leetcode_solutions.xlsx";
        document.body.appendChild(a);
        a.click();

        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error("Error downloading file:", error);
    }
};
