// Kapitel 4: Subscriber in C++ – meldet, wenn gelüftet werden sollte
//   ros2 run sh_grundlagen_cpp raumklima_empfaenger --ros-args -p grenze:=1000
#include <rclcpp/rclcpp.hpp>
#include <sh_interfaces/msg/raumklima.hpp>

using sh_interfaces::msg::Raumklima;

class RaumklimaEmpfaenger : public rclcpp::Node {
public:
    RaumklimaEmpfaenger() : Node("raumklima_empfaenger") {
        grenze_ = declare_parameter<int>("grenze", 1000);
        auto melden = [this](const Raumklima& m) {
            if (m.co2 > grenze_)
                RCLCPP_WARN(get_logger(), "%s: %u ppm CO₂ – bitte lüften", m.raum.c_str(),
                            m.co2);
        };
        sub_ = create_subscription<Raumklima>("raumklima", 10, melden);
    }

private:
    int64_t grenze_;
    rclcpp::Subscription<Raumklima>::SharedPtr sub_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<RaumklimaEmpfaenger>());
    rclcpp::shutdown();
    return 0;
}
