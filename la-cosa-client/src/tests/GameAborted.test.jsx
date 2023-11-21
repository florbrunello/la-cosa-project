import React from 'react';
import { render, act, fireEvent, screen } from '@testing-library/react';
import GameAborted from '../components/game/lobby/gameAborted/GameAborted';
import { describe, expect, test, vi, fn } from "vitest";
import { BrowserRouter } from "react-router-dom";
import MockedSocket from 'socket.io-mock';

describe("GameAborted", () => {
    test("should render", async () => {

        const socketMock = new MockedSocket();
        
        render(
            <BrowserRouter>
                <GameAborted socket={socketMock} />
            </BrowserRouter>
        );

        expect(screen.getByText(/El host abandonó la partida/)).toBeDefined();
        expect(screen.getByText(/Volviendo al menú principal./)).toBeDefined();
    });
});