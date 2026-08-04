#let data = json("data.json")
#let doc = data.document
#let tokens = data.tokens
#let identity = doc.identity

#set page(
  paper: if doc.page_size == "a4" { "a4" } else { "us-letter" },
  margin: (
    top: tokens.margin_top_in * 1in,
    bottom: tokens.margin_bottom_in * 1in,
    left: tokens.margin_left_in * 1in,
    right: tokens.margin_right_in * 1in,
  ),
)
#set text(
  font: tokens.font_family,
  size: tokens.body_size_pt * 1pt,
  fill: rgb(tokens.body_hex),
  hyphenate: true,
)
#set par(leading: 0.65em * tokens.density_scale, justify: false)
#show link: set text(fill: rgb(tokens.accent_hex))

#let heading-text(body) = {
  let t = if tokens.heading_uppercase { upper(body) } else { body }
  text(size: tokens.heading_size_pt * 1pt, weight: "bold", fill: rgb(tokens.accent_hex), t)
}

#let section-heading(label) = {
  v(tokens.section_gap_pt * 1pt)
  heading-text(label)
  v(4pt)
  if tokens.heading_rule {
    line(length: 100%, stroke: 0.6pt + rgb("#cccccc"))
  }
  v(4pt)
}

#let contact-line() = {
  let parts = ()
  if identity.phone != "" { parts.push(identity.phone) }
  if identity.location != "" { parts.push(identity.location) }
  if parts.len() > 0 {
    align(center)[#parts.join(tokens.contact_separator)]
    v(4pt)
  }
  let links = identity.links.map(l => link(l.href)[#l.display_text])
  if links.len() > 0 {
    align(center)[#links.join(tokens.contact_separator)]
    v(6pt)
  }
}

#let date-range(entry) = {
  if entry.date_display != "" {
    align(right)[#text(size: 9.5pt, fill: rgb("#444444"), entry.date_display)]
  }
}

#let bullet-list(items) = {
  if items.len() == 0 { return }
  if tokens.bullet_glyph == "" {
    for item in items {
      par[#item]
      v(tokens.entry_gap_pt * 0.5 * 1pt)
    }
    return
  }
  list(
    marker: tokens.bullet_glyph,
    indent: 12pt,
    body-indent: 6pt,
    spacing: tokens.bullet_leading * 1em,
    ..items.map(item => [#item]),
  )
}

#align(center)[
  #text(
    size: tokens.name_size_pt * 1pt,
    weight: "bold",
    if tokens.name_uppercase { upper(identity.name) } else { identity.name },
  )
]
#contact-line()

#for section in doc.sections {
  section-heading(section.heading)
  if section.kind == "summary" {
    par[#section.summary_text]
  } else if section.kind == "skills" {
    if section.skill_groups.len() > 0 {
      for group in section.skill_groups {
        grid(
          columns: (auto, 1fr),
          column-gutter: 12pt,
          text(weight: "bold", group.label + ":"),
          group.items.join(", "),
        )
        v(tokens.entry_gap_pt * 1pt)
      }
    } else if section.flat_skills.len() > 0 {
      par[#section.flat_skills.join(", ")]
    }
  } else if section.kind == "custom" {
    bullet-list(section.custom_lines)
  } else {
    for entry in section.entries {
      if section.kind == "work_experience" {
        grid(
          columns: (1fr, auto),
          text(weight: "bold", entry.primary),
          date-range(entry),
        )
        grid(
          columns: (1fr, auto),
          entry.secondary,
          if entry.location != "" { text(style: "italic", entry.location) },
        )
        bullet-list(entry.bullets)
      } else if section.kind == "education" {
        grid(
          columns: (1fr, auto),
          text(weight: "bold", entry.primary),
          date-range(entry),
        )
        if entry.secondary != "" { par[#entry.secondary#if entry.location != "" [ — #entry.location]] }
        for line in entry.extra_lines { par[#line] }
      } else if section.kind == "projects" {
        grid(
          columns: (1fr, auto),
          text(weight: "bold", entry.primary + "."),
          date-range(entry),
        )
        if entry.secondary != "" { par[#entry.secondary] }
        bullet-list(entry.bullets)
        if entry.links.len() > 0 {
          par[#link(entry.links.at(0).href)[#entry.links.at(0).display_text]]
        }
      } else if section.kind == "achievements" or section.kind == "publications" {
        grid(
          columns: (1fr, auto),
          text(weight: "bold", entry.primary + "."),
          if entry.date_display != "" { date-range(entry) },
        )
        if entry.bullets.len() > 0 { par[#entry.bullets.join(" ")] }
        if entry.secondary != "" { par[#entry.secondary] }
      }
      v(tokens.entry_gap_pt * 1pt)
    }
  }
}
