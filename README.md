# neurotech-afterimage

When a neurotechnology project stops or changes hands, the public record can leave basic questions unanswered: what happened to the product, what happened to the trial, and what support remained for people using a device. neurotech-afterimage follows those questions through company filings, trial records, published studies, and attributed reporting.

A trial that misses an endpoint does not, by itself, establish that a company or treatment failed. A company closure or asset sale does not show whether each patient continued to receive support. The project follows those distinctions and records gaps when the available evidence cannot answer them.

The collection currently contains 26 individual case dossiers, one synthesis of selected trials, and one extension to that synthesis. It is selective, not a complete history of neurotechnology.

## Explore

- Start with the [case index](INDEX.md).
- See [how sources are weighed and cited](docs/evidence-and-sourcing.md).
- Check the [case-screening notes](docs/case-screening.md) for included and excluded candidates.
- For contribution guidance, read [CONTRIBUTING.md](CONTRIBUTING.md) and use the [dossier template](post-mortems/post-mortem-template.md).

## Local checks

From the project directory, run:

```text
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

These checks catch structural and linking problems. They do not establish that every external source supports every claim; see the [validation record](docs/validation-record.md) for the checks run and their limits.

## License

Original project writing and code are available under [CC BY 4.0](LICENSE). The license does not cover third-party articles, images, trademarks, or other material cited here.
