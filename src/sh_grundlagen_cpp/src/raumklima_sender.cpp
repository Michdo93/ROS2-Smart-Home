// Kapitel 5: derselbe Raumsensor in C++ (rclcpp)
//   ros2 run sh_grundlagen_cpp raumklima_sender --ros-args -p raum:=kueche
#include <chrono>
#include <cmath>
#include <random>
#include <rclcpp/rclcpp.hpp>
#include <sh_interfaces/msg/raumklima.hpp>

using sh_interfaces::msg::Raumklima;
using namespace std::chrono_literals;

class RaumklimaSender : public rclcpp::Node {
public:
    RaumklimaSender() : Node("raumklima_sender") {
        raum_ = declare_parameter<std::string>("raum", "wohnzimmer");
        pub_ = create_publisher<Raumklima>("raumklima", 10);
        timer_ = create_wall_timer(1s, [this] { senden(); });
    }

private:
    void senden() {
        ++schritt_;
        Raumklima m;
        m.header.stamp = now();
        m.raum = raum_;
        m.temperatur = 21.0F + std::sin(schritt_ / 30.0F) + rauschen_(zufall_);
        m.luftfeuchte = 45.0F + 20.0F * rauschen_(zufall_);
        m.co2 = 600 + (schritt_ * 7) % 900;
        pub_->publish(m);
        RCLCPP_INFO(get_logger(), "%s: %.1f °C, %.0f %%, %u ppm", m.raum.c_str(),
                    m.temperatur, m.luftfeuchte, m.co2);
    }

    std::string raum_;
    int schritt_ = 0;
    std::mt19937 zufall_{42};
    std::uniform_real_distribution<float> rauschen_{-0.1F, 0.1F};
    rclcpp::Publisher<Raumklima>::SharedPtr pub_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<RaumklimaSender>());
    rclcpp::shutdown();
    return 0;
}
