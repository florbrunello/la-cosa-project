import { fireEvent, render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { expect, test } from "vitest";
import GameJoinForm from "../components/gameJoinForm/GameJoinForm";
import { BrowserRouter } from "react-router-dom";

describe("GameJoinForm", () => {
  test("should render", async () => {
    render(<BrowserRouter><GameJoinForm /></BrowserRouter>);
   
    expect(screen.getByText("Nombre Jugador")).toBeDefined();
   
    expect(screen.getByRole("button", { name: "Unirse" })).toBeDefined();
  });

  test("should get the data", async () => {
    const utils = render(<BrowserRouter><GameJoinForm /></BrowserRouter>);
    
    const gameName = screen.getByLabelText("Nombre Jugador");

    fireEvent.change(gameName, { target: { value: "NombreTest" } });

    expect(gameName.value).toBe("NombreTest");
  });

  test("should display required error when value is invalid", async () => {
    const utils = render(<BrowserRouter><GameJoinForm /></BrowserRouter>);
    const playerName = screen.getByLabelText("Nombre Jugador");

    const button = screen.getByRole("button", { name: "Unirse" });

    fireEvent.change(playerName, { target: { value: "" } });

    await userEvent.click(button);

    expect(screen.getByText("Nombre requerido")).toBeDefined();
  });

  test("should display error when value has quotation marks", async () => {
    const utils = render(<BrowserRouter><GameJoinForm /></BrowserRouter>);
    
    const playerName = screen.getByLabelText("Nombre Jugador");
   
    const button = screen.getByRole("button", { name: "Unirse" });

    fireEvent.change(playerName, { target: { value: '"NombreTest"' } });

    await userEvent.click(button);

    expect(
      screen.getByText("Nombre del jugador no puede contener comillas")
    ).toBeDefined();

  });

  test("should not display error when value is valid", async () => {
    const utils = render(<BrowserRouter><GameJoinForm /></BrowserRouter>);
   
    const playerName = screen.getByLabelText("Nombre Jugador");
   
    const button = screen.getByRole("button", { name: "Unirse" });

    fireEvent.change(playerName, { target: { value: "NombreTest" } });

    await userEvent.click(button);

    expect(screen.queryByText("Nombre requerido")).toBeNull();
  });
});
