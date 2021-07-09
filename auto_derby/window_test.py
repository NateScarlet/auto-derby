from .clients import DMMClient
from .window import screenshot_pil_crop, screenshot_print_window
import timeit
import cast_unknown as cast


def benchmark_screenshot():
    client = cast.not_none(DMMClient.find())

    run_count = 10
    print_window = (
        timeit.timeit(
            lambda: screenshot_print_window(client.h_wnd),
            number=run_count,
        )
        / run_count
    )
    pil_crop = (
        timeit.timeit(
            lambda: screenshot_pil_crop(client.h_wnd),
            number=run_count,
        )
        / run_count
    )

    print("pil_crop: %.4f print_window: %.4f" % (pil_crop, print_window))
    # pil_crop: 0.3787 print_window: 0.0197
