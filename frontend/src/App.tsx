import Home from "./pages/Home"
import Output from "./pages/Output"
import {BrowserRouter,Routes,Route} from "react-router-dom" 

const App = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Home/>}/>
                <Route path="/" element={<Output/>}/>
            </Routes>
        </BrowserRouter>
    );
}

export default App