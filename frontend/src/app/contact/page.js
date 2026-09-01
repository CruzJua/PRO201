export const metadata = { title: "Contact", description: "Contact the NeuroScan project team." };

export default function ContactPage() {
  return (
    <section className="contact-page shell">
      <div className="contact-intro">
        <p className="eyebrow">Contact / project inquiries</p>
        <h1 className="display page-hero__title">Questions,<br /><em>meet answers.</em></h1>
        <p>Ask about the model, the dataset, or how this prototype was built. We&apos;re happy to talk through the research.</p>
        <div className="contact-index">
          <p><span>Scope</span> Research & education</p>
          <p><span>Response</span> Project team</p>
          <p><span>Clinical care</span> Not provided</p>
        </div>
      </div>

      <form className="contact-form">
        <div className="field-row">
          <label><span>First name</span><input type="text" name="firstName" autoComplete="given-name" placeholder="Ada" /></label>
          <label><span>Last name</span><input type="text" name="lastName" autoComplete="family-name" placeholder="Lovelace" /></label>
        </div>
        <label><span>Email address</span><input type="email" name="email" autoComplete="email" placeholder="ada@example.com" /></label>
        <label><span>Message</span><textarea name="message" rows="6" placeholder="Tell us what you’re working on." /></label>
        <button type="button" className="button button--primary form-button">Send inquiry <span aria-hidden="true">↗</span></button>
        <p className="form-note">Do not include medical records or personal health information.</p>
      </form>
    </section>
  );
}
