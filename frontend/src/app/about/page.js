import Image from "next/image";
import Link from "next/link";

export const metadata = { title: "Method", description: "How the NeuroScan MRI classification research prototype works." };

export default function AboutPage() {
  return (
    <>
      <section className="page-hero shell">
        <p className="eyebrow">Method / 01</p>
        <h1 className="display page-hero__title">A narrow tool for a<br /><em>high-stakes image.</em></h1>
        <p className="page-hero__lede">NeuroScan explores how convolutional neural networks can support rapid, transparent classification of brain MRI images.</p>
      </section>

      <section className="method-visual shell">
        <div className="method-visual__image">
          <Image src="/images/neuroscan-mri-hero.png" alt="Detailed MRI and neural-cell study" fill sizes="(max-width: 800px) 100vw, 62vw" />
        </div>
        <div className="method-visual__caption"><span>Study image / 001</span><p>Axial brain scan with surrounding neural tissue reference.</p></div>
      </section>

      <section className="method-grid shell section-rule">
        <div><p className="eyebrow">What it does</p></div>
        <div className="method-grid__body">
          <h2 className="display display-medium">One model. Four outputs.</h2>
          <p className="method-intro">Each submitted image is resized, normalized, and passed through a trained CNN. The resulting distribution is translated into four readable outcomes: glioma, meningioma, pituitary tumor, or no tumor.</p>
          <div className="method-facts">
            <article><span>01</span><h3>Preprocess</h3><p>Standardize the image into the dimensions and color space expected by the model.</p></article>
            <article><span>02</span><h3>Classify</h3><p>Evaluate learned visual features against the four target classes.</p></article>
            <article><span>03</span><h3>Interpret</h3><p>Expose both the leading label and the probabilities behind it.</p></article>
          </div>
        </div>
      </section>

      <section className="caution-band">
        <p className="eyebrow eyebrow--dark">Important boundary</p>
        <h2 className="display display-medium">A model can flag a pattern. Only a clinician can make a diagnosis.</h2>
        <p>NeuroScan is an educational research prototype. Its output should never replace professional radiology review, clinical context, or medical judgment.</p>
        <Link href="/upload" className="text-link text-link--dark">Try the research tool <span aria-hidden="true">↗</span></Link>
      </section>
    </>
  );
}
