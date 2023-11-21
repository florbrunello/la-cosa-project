import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import CardEffect from "../components/game/cardEffects/CardEffect";
import { set } from "react-hook-form";



describe("CardEffect", () => {
    test("should render", () => {
        const showEffect = {
            showEffect: true,
            data: {
                message: "test",
                cards:[{
                    code: "lla",
                    number_in_card: 1,
                },{
                    code: "lla",
                    number_in_card: 1,
                },{
                    code: "lla",
                    number_in_card: 1,
                }]
            },
            type: "whisky"
        };

        const setShowEffect = vi.fn();

        render(<CardEffect 
            showEffect={showEffect}
            setShowEffect={setShowEffect}/>
        );

        expect(setShowEffect).toHaveBeenCalledTimes(0);
    });
});