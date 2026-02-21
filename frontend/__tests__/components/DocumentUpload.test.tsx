import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DocumentUpload } from "../../components/documents/DocumentUpload";

describe("DocumentUpload", () => {
  it("calls onUpload when file selected", async () => {
    const onUpload = vi.fn().mockResolvedValue(undefined);
    render(<DocumentUpload onUpload={onUpload} />);

    const input = screen.getByTestId("upload-input") as HTMLInputElement;
    const file = new File(["content"], "test.txt", { type: "text/plain" });
    fireEvent.change(input, { target: { files: [file] } });

    expect(onUpload).toHaveBeenCalledTimes(1);
    expect(onUpload).toHaveBeenCalledWith(file);
  });
});
