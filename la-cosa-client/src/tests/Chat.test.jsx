//testear que se renderice el boton. el input y el div de los mensajes
//probar que si el input esta vacio no se envie el mensaje
//probar que si el input tiene solo espacios no se envie el mensaje
//probar que si el input tiene comillas no se envie el mensaje
//probar que renderice el mensaje enviado


import MockedSocket from 'socket.io-mock';
import { fireEvent, render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { expect, test } from "vitest";
import Chat from "../components/game/chat/Chat";

describe("Chat", () => {
  test("should render", async () => {
    const socketMock = new MockedSocket();
    const utils = render(<Chat  socket={socketMock}/>);
    expect(screen.getByRole("button", { name: "Enviar" })).toBeDefined();
  });

  test("should display required error when value is invalid", async () => {
    const socketMock = new MockedSocket();
    const utils = render(<Chat socket={socketMock} gameId={1} playerName={'player1'}/>);
    
    const message = screen.getByTestId("input");
    const button = screen.getByRole("button", { name: "Enviar" });

    fireEvent.change(message, { target: { value: "" } });

    await userEvent.click(button);

    expect(screen.getByText("Mensaje requerido")).toBeDefined();
  });


  test("should display required error when value has quotation marks", async () => {
    const socketMock = new MockedSocket();
    const utils = render(<Chat socket={socketMock} gameId={1} playerName={'player1'}/>);
    
    const message = screen.getByTestId("input");
    const button = screen.getByRole("button", { name: "Enviar" });

    fireEvent.change(message, { target: { value: '"LaCosa"'}});

    await userEvent.click(button);

    expect(screen.getByText("No puede contener comillas")).toBeDefined();
  });

  test("should not display error when value is valid", async () => {
    const socketMock = new MockedSocket();
    const utils = render(<Chat socket={socketMock} gameId={1} playerName={'player1'}/>);
    
    const message = screen.getByTestId("input");
    const button = screen.getByRole("button", { name: "Enviar" });

    fireEvent.change(message, { target: { value: "LaCosa"}});

    await userEvent.click(button);

    expect(screen.queryByText("Nombre requerido")).toBeNull();
  });

});
