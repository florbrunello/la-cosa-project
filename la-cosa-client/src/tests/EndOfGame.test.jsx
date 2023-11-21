import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import EndOfGame from "../components/endOfGame/EndOfGame";
import { BrowserRouter } from "react-router-dom";

const mockSocket = {
    disconnect: vi.fn(),
    on: vi.fn()
}

describe("EndOfGame", () => {
    test("should render", async () => {
        render(<BrowserRouter><EndOfGame socket={mockSocket}/></BrowserRouter>);
        expect(screen.getByTestId("text")).toBeDefined(); 
        expect(screen.getByRole("button", { name: "Abandonar Partida" })).toBeDefined();
    });
});
