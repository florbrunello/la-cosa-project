//Check if name has quotation marks
export const valueHasQuotationMarks = (name) => {
  const nameTrimmed = name.trim();
  return nameTrimmed.includes('"');
};
