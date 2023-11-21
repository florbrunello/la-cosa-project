import { expect, test, vi } from "vitest";
import FunctionButton from "../components/functionButton/FunctionButton";
import {fireEvent, render, screen} from '@testing-library/react';


describe("FunctionButton", () => {

    test("should show the text all the time", ()=>{
        render(
            <FunctionButton
                text="Hello"
                onClick={() => {}}
            />
        );
        expect(screen.getByText("Hello")).toBeDefined();
    });

    test("should execute the funtion when is clicked", ()=>{
        const printSpy = vi.spyOn(console, "log");
        
        render(
            <FunctionButton
            text="Hello"
            onClick = {() => {printSpy()}}
            />
            );
            
        const button = screen.getByText("Hello");
        expect(printSpy).not.toHaveBeenCalled();
        
        fireEvent.click(button);
        expect(printSpy).toHaveBeenCalled();
        expect(printSpy).not.toHaveBeenCalledTimes(2);
    });


})

