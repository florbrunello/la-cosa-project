import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import DeadPlayer from "../components/game/deadPlayer/DeadPlayer";
import { BrowserRouter } from "react-router-dom";



describe("GameCreationForm", () => {
    test("should render", async () => {
        const disconnect = vi.fn();
        render(<BrowserRouter>
            <DeadPlayer socket={{disconnect}}/>
        </BrowserRouter>);
        //expect(screen.getByText("¡Has sido incinerado!")).toBeDefined();
        const button = screen.getByRole("button", { name: "Salir de la Partida" });
        expect(button).toBeDefined();
        fireEvent.click(button);
        expect(disconnect).toHaveBeenCalledTimes(1);
    });
});
