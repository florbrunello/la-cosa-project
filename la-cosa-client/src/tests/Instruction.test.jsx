import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, expect, test } from "vitest";
import Instruction from '../components/game/instruction/Instruction';

describe("Instruction", () => {
    test("should render case 0", async () => {        
        render(
            <Instruction state={0} cardSelected={{}}/>
        );
        expect(screen.getByTestId("case-0")).toBeDefined();
    });

    test("should render case 1 with cardSelected", async () => {        
        render(
            <Instruction state={1} cardSelected={{}}/>
        );
        expect(screen.getByTestId("case-1-not-card-selected")).toBeDefined();
    });
    
    test("should render case 1 with !cardSelected", async () => {        
        render(
            <Instruction state={1} cardSelected={{code: 1}}/>
        );
        expect(screen.getByTestId("case-1-card-selected")).toBeDefined();
    });

    test("should render case 2", async () => {        
        render(
            <Instruction state={2} cardSelected={{}}/>
        );
        expect(screen.getByTestId("case-2")).toBeDefined();
    });

    test("should render case 3", async () => {        
        render(
            <Instruction state={3} cardSelected={{}}/>
        );
        expect(screen.getByTestId("case-3")).toBeDefined();
    });

    test("should render case 4", async () => {        
        render(
            <Instruction state={4} cardSelected={{}}/>
        );
        expect(screen.getByTestId("case-4")).toBeDefined();
    });

    test("should render case 6", async () => {        
        render(
            <Instruction state={6} cardSelected={{}}/>
        );
        expect(screen.getByTestId("case-6")).toBeDefined();
    });
});