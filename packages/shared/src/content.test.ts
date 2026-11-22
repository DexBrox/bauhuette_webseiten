import { describe, expect, it } from "vitest";
import { ContactRequestSchema, parsePage } from "./index";

const valid = {
  title: "Start",
  description: "Die Startseite",
  sections: [{ id: "willkommen", heading: "Willkommen", text: "Hallo" }],
};

describe("parsePage", () => {
  it("akzeptiert gültige Inhalte", () => {
    expect(parsePage(valid, "test.json").title).toBe("Start");
  });

  it("meldet fehlende Bildbeschreibung verständlich", () => {
    const withoutAlt = {
      ...valid,
      sections: [{ ...valid.sections[0], image: { src: "a.jpg", alt: "" } }],
    };
    expect(() => parsePage(withoutAlt, "home.json")).toThrow(/home\.json.*Bildbeschreibung fehlt/);
  });
});

describe("ContactRequestSchema", () => {
  it("lehnt ausgefüllten Honigtopf ab", () => {
    const request = {
      name: "Vale",
      email: "vale@example.org",
      message: "Hallo, eine Frage.",
      website: "spam",
    };
    expect(ContactRequestSchema.safeParse(request).success).toBe(false);
  });
});
