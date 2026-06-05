export function Disclaimer({ text }: { text?: string }) {
  const defaultDisclaimer = "Disclaimer: This is general meal inspiration only. Nutrition information is approximate and for informational purposes. It is not a substitute for professional medical or dietary advice. If you have any medical condition, are pregnant, breastfeeding, or taking medication, please consult a qualified doctor or registered dietitian before making dietary changes.";
  return (
    <div className="disclaimer-box text-sm">
      {text || defaultDisclaimer}
    </div>
  );
}
