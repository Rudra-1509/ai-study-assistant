import type {StudyInput,StudyResponse} from "../types/study";
const API_BASE_URL = "http://127.0.0.1:8000";

export async function analyze(input:StudyInput):Promise<StudyResponse> {
         const formData=new FormData();

        if(input.input_type==="text"){
            formData.append("input_type","text");
            formData.append("content",input.content);
        }
        if(input.input_type==="pdf"){
            formData.append("input_type","pdf");
            formData.append("content",input.file);
        }
        if(input.input_type==="pdf"){
            formData.append("input_type","pdf");
            formData.append("content",input.file);
        }
    const response=await fetch(`${API_BASE_URL}/analyze`,{method:"POST",body:formData});

    if(!response.ok){
        const errorText = await response.text();
        throw new Error(errorText || "Failed to analyze input");
    }

    return response.json();
}

