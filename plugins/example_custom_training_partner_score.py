import auto_derby
from auto_derby import single_mode, template


def _is_wanted_partner(partner: single_mode.training.Partner) -> bool:
    partner_icon_img = template.screenshot().crop(partner.icon_bbox)
    # custom logic here to compare partner icon image
    _ = partner_icon_img

    return False


class Partner(single_mode.training.Partner):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)
        if _is_wanted_partner(self):
            ret += 3
        return ret


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.single_mode_training_partner_class = Partner


auto_derby.plugin.register(__name__, Plugin())
