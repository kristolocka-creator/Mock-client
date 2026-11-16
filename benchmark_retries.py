import random
import time

from tenacity import retry, stop_after_attempt, wait_exponential


TOTAL_REQUESTS = 100

def create_scenarios():
    scenarios = []

    for _ in range(TOTAL_REQUESTS):
        scenario = []

        while True:
            if random.random() < 0.3:
                scenario.append(False)
            else:
                scenario.append(True)
                break

        scenarios.append(scenario)

    return scenarios

def fake_request(scenario):
    if not scenario:
        raise RuntimeError("Temporary error")

    result = scenario.pop(0)

    if not result:
        raise RuntimeError("Temporary error")

    return [0.1, 0.2, 0.3]


def request_without_retry(scenario):
    try:
        fake_request(scenario)
        return True
    except RuntimeError:
        return False


def request_with_manual_retry(
    scenario,
    max_retries=3,
    initial_delay=0.001,
    multiplier=2
):
    delay = initial_delay

    for attempt in range(max_retries + 1):
        try:
            fake_request(scenario)
            return True

        except RuntimeError:
            if attempt == max_retries:
                return False

            time.sleep(delay)
            delay *= multiplier

    return False


def create_tenacity_request(scenario, max_retries):
    @retry(
        stop=stop_after_attempt(max_retries + 1),
        wait=wait_exponential(multiplier=0.001)
    )
    def request():
        fake_request(scenario)
        return True

    return request


def run_benchmark(name, request_function, scenarios):
    successful = 0
    failed = 0

    start_time = time.perf_counter()

    for scenario in scenarios:
        try:
            result = request_function(scenario)

            if result:
                successful += 1
            else:
                failed += 1

        except Exception:
            failed += 1

    elapsed = time.perf_counter() - start_time

    print(
        f"{name:<25}"
        f"{successful:<12}"
        f"{failed:<10}"
        f"{elapsed:.4f} sec"
    )


def main():
    scenarios = create_scenarios()

    print(
        f"{'Method':<25}"
        f"{'Successful':<12}"
        f"{'Failed':<10}"
        f"Time"
    )

    print("-" * 57)

    run_benchmark(
        "No retry",
        request_without_retry,
        [scenario.copy() for scenario in scenarios]
    )

    for max_retries in (0, 1, 3):
        run_benchmark(
            f"Manual retry ({max_retries})",
            lambda scenario, retries=max_retries: request_with_manual_retry(
                scenario,
                max_retries=retries
            ),
            [scenario.copy() for scenario in scenarios]
        )

    for max_retries in (1, 3):
        run_benchmark(
            f"Tenacity ({max_retries})",
            lambda scenario, retries=max_retries: create_tenacity_request(
                scenario,
                retries
            )(),
            [scenario.copy() for scenario in scenarios]
        )


if __name__ == "__main__":
    main()