import Image from "next/image";
import Link from "next/link";

const steps = [
  { number: "01", title: "Add the scan", text: "Select a brain MRI image in JPG or PNG format from your device." },
  { number: "02", title: "Run inference", text: "The model normalizes the image and evaluates it across four learned classes." },
  { number: "03", title: "Read the signal", text: "Review the leading classification, confidence, and full probability distribution." },
];

const classes = ["Glioma", "Meningioma", "Pituitary", "No tumor"];

export default function Home() {
  return (
    <>
      <section className="hero shell">
        <div className="hero__copy">
          <p className="eyebrow">AI-assisted image classification / v1.0</p>
          <h1 className="display hero__title">Machine vision<br />for the <em>human brain.</em></h1>
          <div className="hero__intro">
            <p>A focused research tool for classifying brain MRI images and surfacing the model&apos;s confidence in seconds.</p>
            <Link href="/upload" className="button button--primary">Analyze an MRI <span aria-hidden="true">↗</span></Link>
          </div>
        </div>

        <figure className="hero-visual">
          <Image src="/images/neuroscan-mri-hero.png" alt="Monochrome brain MRI cross-section surrounded by microscopic neural cells" fill priority sizes="(max-width: 800px) 100vw, 54vw" />
          <figcaption><span>FIG. 01</span><span>Axial MRI / neural field</span></figcaption>
        </figure>
      </section>

      <section className="signal-band" aria-label="Classifier summary">
        <div className="signal-band__label"><span className="signal-dot" aria-hidden="true" />Model scope</div>
        <div className="signal-band__classes">
          {classes.map((item, index) => <p key={item}><span>{String(index + 1).padStart(2, "0")}</span>{item}</p>)}
        </div>
      </section>

      <section className="process shell section-rule">
        <div className="section-heading">
          <p className="eyebrow">The process / three moves</p>
          <h2 className="display display-medium">From image to signal.</h2>
          <p className="section-heading__aside">The interface stays intentionally simple so the output—not the software—gets your attention.</p>
        </div>
        <div className="process-grid">
          {steps.map((step) => (
            <article className="process-step" key={step.number}>
              <p className="process-step__number">{step.number}</p>
              <div><h3>{step.title}</h3><p>{step.text}</p></div>
            </article>
          ))}
        </div>
      </section>

      <section className="feature-split">
        <div className="feature-split__statement">
          <p className="eyebrow eyebrow--dark">Built for focus</p>
          <h2 className="display display-medium">Less interface.<br />More <em>evidence.</em></h2>
        </div>
        <div className="feature-split__details">
          <article><span>01 / Direct</span><h3>No dashboard detour</h3><p>Upload, analyze, and review the output from one working surface.</p></article>
          <article><span>02 / Legible</span><h3>Confidence in context</h3><p>Every class probability remains visible instead of hiding behind one answer.</p></article>
          <article><span>03 / Responsible</span><h3>A research signal, not a verdict</h3><p>Results are clearly framed as educational and never as a clinical diagnosis.</p></article>
        </div>
      </section>

      <section className="closing-cta shell">
        <p className="eyebrow">Ready when you are</p>
        <h2 className="display display-large">Bring the scan.<br />We&apos;ll surface the signal.</h2>
        <Link href="/upload" className="button button--outline">Start analysis <span aria-hidden="true">→</span></Link>
      </section>
    </>
  );
}
